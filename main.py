from app.logger import setup_logger
from classes.Config import app_config
from classes.Manager import manager
from app.telegram import tg_start, tg_stop, tg_users

import asyncio
import signal
import time
from loguru import logger


shutdown_event = asyncio.Event()
sleep_event = asyncio.Event()


@logger.catch
def sigint_handler() -> None:
    logger.warning(f"Operating SIGINT call!")
    shutdown_event.set()
    sleep_event.set()


@logger.catch
def sigterm_handler() -> None:
    logger.warning(f"Operating SIGTERM call!")
    shutdown_event.set()
    sleep_event.set()


@logger.catch
async def main() -> None:
    aio_loop = asyncio.get_event_loop()

    aio_loop.add_signal_handler(
        sig=signal.SIGINT,
        callback=sigint_handler
    )

    aio_loop.add_signal_handler(
        sig=signal.SIGTERM,
        callback=sigterm_handler
    )

    await tg_start()
    await tg_users(t=manager.get_tg_list_users())

    logger.info(f"Entering main loop with {app_config.loop_sleep_seconds:,} seconds timeout...")
    time_acc = 0
    while not shutdown_event.is_set():
        logger.info(f"Main loop executing:")
        start_time = int(
            time.time()
        )

        for user in manager.user_list:
            user_name = manager.user_list[user].get_user_name()
            try:
                await manager.user_list[user].operate_info()
            except BaseException as e:
                logger.error(f"Cannot update or operate info for user {user_name}: {e}")
            else:
                logger.info(f"Successfully updated and operated info for user {user_name}")

            try:
                await manager.user_list[user].operate_workers()
            except BaseException as e:
                logger.error(f"Cannot update or operate workers for user {user_name}: {e}")
            else:
                logger.info(f"Successfully updated and operated workers for user {user_name}")


        logger.info(f"Going to sleep for {app_config.loop_sleep_seconds:,} seconds...")
        try:
            await asyncio.wait_for(
                fut=sleep_event.wait(),
                timeout=app_config.loop_sleep_seconds
            )
        except asyncio.TimeoutError:
            pass

        end_time = int(
            time.time()
        )
        time_acc += (end_time - start_time)
        if time_acc >= 24*60*60:
            time_acc = 0
            for user in manager.user_list:
                if manager.user_list[user].daily_statistics:
                    user_name = manager.user_list[user].get_user_name()
                    try:
                        await manager.user_list[user].tg_daily_statistics()
                    except BaseException as e:
                        logger.error(f"Cannot send daily statistics for user {user_name}: {e}")
                    else:
                        logger.info(f"Successfully sent daily statistics for user {user_name}")

    logger.critical(f"Exited main loop!")
    await tg_stop()

    return None


if __name__ == "__main__":
    setup_logger()

    logger.debug(f"{app_config=}")
    logger.debug(f"{manager.user_list=}")

    asyncio.run(
        main=main()
    )
