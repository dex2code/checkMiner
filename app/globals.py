from loguru import logger
import asyncio


shutdown_event = asyncio.Event()
sleep_event = asyncio.Event()


@logger.catch
def sigint_handler() -> None:
    logger.info(f"Operating SIGINT call!")
    shutdown_event.set()
    sleep_event.set()


@logger.catch
def sigterm_handler() -> None:
    logger.info(f"Operating SIGTERM call!")
    shutdown_event.set()
    sleep_event.set()


if __name__ == "__main__":
    pass
