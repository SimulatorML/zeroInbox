import logging
import asyncio
from aiogram import Bot, Dispatcher
from src.models.gpt_classifier import GptClassifier
from src.models.embedder import TextEmbedder
from src.bot.handlers import topic_commands, msg_commands
from src.config import BOT_TOKEN, DB_PARAMS
from database.pg_connector import PgConnector

class CatBot:
    """
    A Telegram bot that integrates GPT-based classification and text embedding for managing and categorizing messages.
    It uses PostgreSQL for database operations, ensuring message and topic management are persistent and organized.

    Attributes:
        bot (Bot): The Telegram Bot instance.
        dp (Dispatcher): The Aiogram Dispatcher that handles the routing of incoming messages.
        classifier (GptClassifier): The GPT model for message classification.
        embedder (TextEmbedder): The model for embedding text messages to vector space.
        db_conn (PgConnector): The connector for PostgreSQL database interactions.

    Methods:
        __init__: Constructs the necessary components for the bot, including the database connection.
        start: Initiates the bot, including starting the polling process and including necessary routers.
    """
    def __init__(self):
        """
        Initializes the CatBot instance by setting up the bot token, classifiers, embedder, and database connection.
        Raises:
            RuntimeError: If the database connection fails, it raises a RuntimeError with the error message.
        """
        self.bot = Bot(token=BOT_TOKEN)
        self.dp = Dispatcher()
        self.classifier = GptClassifier([])
        self.embedder = TextEmbedder()

        try:
            self.db_conn = PgConnector(**DB_PARAMS)
        except Exception as e:
            raise RuntimeError(f'Database connection error: {e}')


    async def start(self):
        """
        Initializes the bot's command routers and starts polling for updates. This method sets up the environment
        for the bot to begin receiving and responding to messages.
        """
        self.dp.include_routers(topic_commands.router, msg_commands.router)
        await self.dp.start_polling(self.bot, embedder = self.embedder, classifier = self.classifier)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    bot = CatBot()
    asyncio.run(bot.start())
