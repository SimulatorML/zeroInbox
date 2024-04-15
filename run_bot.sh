#!/bin/bash
export PYTHONPATH=$(pwd)
export OPENAI_API_KEY=''
export BOT_TOKEN=''
export db_host=''
export db_name=''
export db_port=5432
export db_user=''
export db_pwd=''

python src/bot/bot.py