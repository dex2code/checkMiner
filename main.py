from app.config import app_config
from app.logger import setup_logger
from classes.Manager import manager
from app.main import main

import asyncio
from loguru import logger


if __name__ == "__main__":
    setup_logger()

    logger.debug(f"{app_config=}")
    logger.debug(f"{manager.user_list=}")

    asyncio.run(
        main=main()
    )
