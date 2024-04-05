import logging
import asyncio
from aiogram import Bot, Dispatcher
from src.models.gpt_classifier import GptClassifier
from src.bot.handlers import auth, commands
from src.config import BOT_TOKEN, DB_PARAMS
from database.pg_connector import PgConnector

class CatBot:
    """
    A Telegram bot that categorizes messages using a GPT-based classifier.

    Attributes:
        bot (Bot): An instance of the aiogram Bot class, initialized with the bot's token.
        dp (Dispatcher): An instance of the aiogram Dispatcher class, used to manage event handlers.
        classifier (GptClassifier): An instance of a GPT-based classifier for categorizing messages.
    """
    def __init__(self):
        """Initializes the CatBot instance."""
        self.bot = Bot(token=BOT_TOKEN)
        self.dp = Dispatcher()
        self.classifier = GptClassifier()

        try:
            self.db_conn = PgConnector(**DB_PARAMS)
        except Exception as e:
            raise RuntimeError(f'Database connection error: {e}')


    async def start(self):
        """Initializes the bot's command routers and starts polling for updates."""
        self.dp.include_routers(commands.router, auth.router)
        await self.dp.start_polling(self.bot, classifier = self.classifier)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    bot = CatBot()
    asyncio.run(bot.start())
