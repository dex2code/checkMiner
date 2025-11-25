from app.config import app_config

from loguru import logger
import sys


@logger.catch
def setup_logger() -> None:
    logger.remove()

    logger.add(
        sink=sys.stderr,
        level=app_config.logger.level,
        colorize=True
    )

    logger.add(
        sink=app_config.logger.path,
        level=app_config.logger.level,
        rotation=app_config.logger.rotation,
        retention=app_config.logger.retention,
        serialize=app_config.logger.serialize
    )

    logger.info(f"Logging started")

    return None


if __name__ == "__main__":
    pass
