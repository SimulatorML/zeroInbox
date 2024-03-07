import logging
import asyncio
from aiogram import Bot, Dispatcher
from src.models.gpt_classifier import GptClassifier
from src.test_bot.handlers import messages, commands
from src.config import TEST_BOT_TOKEN

class TestCatBot:
    """A class representing a test bot for checking the categorization of Telegram messages."""
    def __init__(self):
        """Initializes the TestBot instance."""
        self.bot = Bot(token=TEST_BOT_TOKEN)
        self.dp = Dispatcher()
        self.classifier = GptClassifier()

    async def start(self):
        """Starts the bot's event loop for handling messages and commands."""
        self.dp.include_routers(commands.router, messages.router)
        await self.dp.start_polling(self.bot, classifier = self.classifier)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    bot = TestCatBot()
    asyncio.run(bot.start())
