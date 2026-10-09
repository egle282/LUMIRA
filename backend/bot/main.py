import os
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from .handlers import onboarding, chat
import asyncio
from backend.core.logger import logger

async def start_bot():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN is not set")
        return

    bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    # Register handlers
    dp.include_router(onboarding.router)
    dp.include_router(chat.router)

    logger.info("Starting Telegram Bot Polling")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(start_bot())
