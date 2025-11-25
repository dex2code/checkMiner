from app.config import app_config
from app.globals import sigint_handler, sigterm_handler
from app.globals import sleep_event, shutdown_event
from classes.Manager import manager
from app.telegram import tg_bot_shutdown
from app.info import operate_info
from app.workers import operate_workers

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

        for user in manager.user_list:
            await operate_info(user=user)
            await operate_workers(user=user)

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
