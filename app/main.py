from app.config import app_config
from app.globals import sigint_handler, sigterm_handler
from app.globals import sleep_event, shutdown_event
from classes.UserManager import user_manager
from app.tools import convert_hashrate
from app.telegram import tg_bot_shutdown

from loguru import logger
import asyncio
import signal


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


    logger.info(f"Entering main loop with {app_config.loop_sleep_seconds:,} seconds timeout...")
    while not shutdown_event.is_set():
        logger.info(f"Main loop executing:")

        for user_addr in user_manager.user_list:
            user_name = user_manager.user_list[user_addr].get_user_name()

            logger.info(f"Updating info for user {user_name}...")
            logger.debug(f"{user_manager.user_list[user_addr].info}")
            info_flag = user_manager.user_list[user_addr].info_flag
            old_balance = user_manager.user_list[user_addr].info.final_balance
            try:
                await user_manager.user_list[user_addr].update_info()
            
            except Exception as e:
                logger.exception(f"Cannot update info for user {user_name}: {e} ({info_flag=})")
                if not info_flag:
                    user_manager.user_list[user_addr].set_info_flag(v=True)
                    # Inform Balance API Error
            
            else:
                logger.info(f"Successfully updated info for user {user_name} ({info_flag=})")
                logger.debug(f"{user_manager.user_list[user_addr].info}")

                new_balance = user_manager.user_list[user_addr].info.final_balance

                if info_flag:
                    user_manager.user_list[user_addr].set_info_flag(v=False)
                    # inform Balance API Ok with current balance

                if old_balance != new_balance:
                    logger.warning(f"Balance changed for user {user_name}: {old_balance:,} -> {new_balance:,}")
                    # Inform balance change
                else:
                    logger.info(f"Balance for user {user_name} is the same: {new_balance:,}")


            logger.info(f"Updating workers for user {user_name}...")
            logger.debug(f"{user_manager.user_list[user_addr].workers}")
            workers_flag = user_manager.user_list[user_addr].workers_flag
            old_number_workers = user_manager.user_list[user_addr].workers.workers
            try:
                await user_manager.user_list[user_addr].update_workers()
            
            except Exception as e:
                logger.exception(f"Cannot update workers for user {user_name}: {e} ({workers_flag=})")
                if not workers_flag:
                    user_manager.user_list[user_addr].set_workers_flag(v=True)
                    # Inform Workers API Error

            else:
                logger.info(f"Successfully updated workers for user {user_name} ({workers_flag=})")
                logger.debug(f"{user_manager.user_list[user_addr].workers}")

                new_number_workers = user_manager.user_list[user_addr].workers.workers

                if workers_flag:
                    user_manager.user_list[user_addr].set_workers_flag(v=False)
                    # Inform Workers API OK with current number of workers

                if old_number_workers != new_number_workers:
                    logger.warning(f"Number of workers for user {user_name} changed: {old_number_workers} -> {new_number_workers}")
                    # Inform number of workers changed
                else:
                    logger.info(f"Number of workers for user {user_name} is the same: {new_number_workers}")


                try:
                    cur_hashrate1m_str = user_manager.user_list[user_addr].workers.hashrate1m
                    cur_hashrate1m_int = user_manager.user_list[user_addr].workers.get_hashrate1m_int()
                    tr_hashrate1m_str = app_config.pool_users[user_addr].hashrate1m_treshold
                    tr_hashrate1m_int = convert_hashrate(tr_hashrate1m_str)
                    flag_hashrate1m = user_manager.user_list[user_addr].hashrate1m_flag

                    if cur_hashrate1m_int < tr_hashrate1m_int:
                        logger.warning(f"1m hashrate for user {user_name} is lower than expected: {cur_hashrate1m_str} < {tr_hashrate1m_str} ({flag_hashrate1m=})")

                        if not flag_hashrate1m:
                            user_manager.user_list[user_addr].set_hashrate1m_flag(v=True)
                            # Inform Hashrate 1m LOW

                    else:
                        logger.info(f"1m hashrate for user {user_name} is OK: {cur_hashrate1m_str} >= {tr_hashrate1m_str} ({flag_hashrate1m=})")

                        if flag_hashrate1m:
                            user_manager.user_list[user_addr].set_hashrate1m_flag(v=False)
                            # Inform Hashrate 1m OK

                except Exception as e:
                    flag_hashrate1m = user_manager.user_list[user_addr].hashrate1m_flag
                    logger.exception(f"Cannot compare hashrate1m for user {user_name}: {e}\n ({flag_hashrate1m=})")
                
                else:
                    flag_hashrate1m = user_manager.user_list[user_addr].hashrate1m_flag
                    logger.info(f"Successfully measured hashrate1m ({flag_hashrate1m=})")


                try:
                    cur_hashrate5m_str = user_manager.user_list[user_addr].workers.hashrate5m
                    cur_hashrate5m_int = user_manager.user_list[user_addr].workers.get_hashrate5m_int()
                    tr_hashrate5m_str = app_config.pool_users[user_addr].hashrate5m_treshold
                    tr_hashrate5m_int = convert_hashrate(tr_hashrate5m_str)
                    flag_hashrate5m = user_manager.user_list[user_addr].hashrate5m_flag

                    if cur_hashrate5m_int < tr_hashrate5m_int:
                        logger.warning(f"5m hashrate for user {user_name} is lower than expected: {cur_hashrate5m_str} < {tr_hashrate5m_str} ({flag_hashrate5m=})")

                        if not user_manager.user_list[user_addr].hashrate5m_flag:
                            user_manager.user_list[user_addr].set_hashrate5m_flag(v=True)
                            # Inform hashrate 5m is LOW

                    else:
                        logger.info(f"5m hashrate for user {user_name} is OK: {cur_hashrate5m_str} >= {tr_hashrate5m_str} ({flag_hashrate5m=})")

                        if user_manager.user_list[user_addr].hashrate5m_flag:
                            user_manager.user_list[user_addr].set_hashrate5m_flag(v=False)
                            # Inform hashrate 5m is OK

                except Exception as e:
                    flag_hashrate5m = user_manager.user_list[user_addr].hashrate5m_flag
                    logger.exception(f"Cannot compare hashrate5m for user {user_name}: {e}")
                
                else:
                    flag_hashrate5m = user_manager.user_list[user_addr].hashrate5m_flag
                    logger.info(f"Successfully measured hashrate5m ({flag_hashrate5m=})")


                try:
                    cur_hashrate1hr_str = user_manager.user_list[user_addr].workers.hashrate1hr
                    cur_hashrate1hr_int = user_manager.user_list[user_addr].workers.get_hashrate1hr_int()
                    tr_hashrate1hr_str = app_config.pool_users[user_addr].hashrate1hr_treshold
                    tr_hashrate1hr_int = convert_hashrate(tr_hashrate1hr_str)
                    flag_hashrate1hr = user_manager.user_list[user_addr].hashrate1hr_flag

                    if cur_hashrate1hr_int < tr_hashrate1hr_int:
                        logger.warning(f"1hr hashrate for user {user_name} is lower than expected: {cur_hashrate1hr_str} < {tr_hashrate1hr_str} ({flag_hashrate1hr=})")

                        if not user_manager.user_list[user_addr].hashrate1hr_flag:
                            user_manager.user_list[user_addr].set_hashrate1hr_flag(v=True)
                            # Inform hashrate 1hr is LOW

                    else:
                        logger.info(f"1hr hashrate for user {user_name} is OK: {cur_hashrate1hr_str} >= {tr_hashrate1hr_str} ({flag_hashrate1hr=})")

                        if user_manager.user_list[user_addr].hashrate1hr_flag:
                            user_manager.user_list[user_addr].set_hashrate1hr_flag(v=False)
                            # Inform hashrate 1h is OK

                except Exception as e:
                    flag_hashrate1hr = user_manager.user_list[user_addr].hashrate1hr_flag
                    logger.exception(f"Cannot compare hashrate1hr for user {user_name}: {e}")
                
                else:
                    flag_hashrate1hr = user_manager.user_list[user_addr].hashrate1hr_flag
                    logger.info(f"Successfully measured hashrate1hr ({flag_hashrate1hr=})")


        logger.info(f"Going to sleep for {app_config.loop_sleep_seconds:,} seconds...")
        try:
            await asyncio.wait_for(
                fut=sleep_event.wait(),
                timeout=app_config.loop_sleep_seconds
            )
        except asyncio.TimeoutError:
            pass

    logger.warning(f"Exiting main loop!")
    await tg_bot_shutdown()

    return None


if __name__ == "__main__":
    pass