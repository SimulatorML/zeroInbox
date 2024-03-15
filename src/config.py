import os
from dotenv import load_dotenv

# os env. variables
load_dotenv()

TEST_BOT_TOKEN = os.getenv('TEST_BOT_TOKEN')

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise RuntimeError('OPENAI_API_KEY environment variable is not set.')

GPT_VERSION = 'gpt-3.5-turbo-0125'

OPENAI_OPTIONS = {
    "temperature": 0.1,
    "max_tokens": 8
}
