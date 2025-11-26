from app.config import app_config

from loguru import logger
from aiogram import Bot
import asyncio


bot = Bot(
    token=app_config.TG_BOT_TOKEN.get_secret_value()
)


@logger.catch
async def send_message(t: str) -> None:
    logger.info(f"Sending message: {t}")
    await bot.send_message(
        chat_id=app_config.TG_CHAT_ID.get_secret_value(),
        text=f"{app_config.bot_nickname}:\n{t}"
    )
    await asyncio.sleep(delay=2.1)
    return None


@logger.catch
async def tg_start() -> None:
    await send_message(f"⚡ Service Started!")
    return None


@logger.catch
async def tg_users(t: str) -> None:
    await send_message(f"👀 Watching for:\n{t}")
    return None


@logger.catch
async def tg_stop() -> None:
    await send_message(f"❌ Service stopped!")
    await bot.session.close()
    logger.warning(f"TG Bot is stopped")
    return None


if __name__ == "__main__":
    pass
