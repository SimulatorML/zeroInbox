import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise RuntimeError('BOT_TOKEN environment variable is not set.')

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise RuntimeError('OPENAI_API_KEY environment variable is not set.')

GPT_VERSION = 'gpt-3.5-turbo-0125'

OPENAI_OPTIONS = {
    "temperature": 0.1,
    "max_tokens": 8
}

DB_PARAMS = {
    'host': os.getenv('db_host'),
    'database': os.getenv('db_name'),
    'port': int(os.getenv('db_port')),
    'user': os.getenv('db_user'),
    'password': os.getenv('db_pwd')
}

if not all(DB_PARAMS.values()):
    raise RuntimeError('Database parameters environment variables are not set.')
