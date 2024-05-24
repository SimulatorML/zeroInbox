#!/bin/bash
export PYTHONPATH=$(pwd)
export OPENAI_API_KEY=''
export BOT_TOKEN=''
export db_host='0.0.0.0'
export db_name='db'
export db_port=5432
export db_user='user'
export db_pwd='password'

python src/bot/bot.py