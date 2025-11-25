from app.config import app_config

from loguru import logger
from aiogram import Bot


bot = Bot(
    token=app_config.TG_BOT_TOKEN.get_secret_value()
)


@logger.catch
async def tg_bot_shutdown() -> None:
    logger.warning(f"Shutting down TG Bot...")
    await bot.session.close()
    logger.warning(f"TG Bot is stopped")


if __name__ == "__main__":
    pass
