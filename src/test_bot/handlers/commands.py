from aiogram.filters.command import Command
from aiogram import Router
from aiogram.types import Message

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    """Message on bot startup"""
    msg = [
        'Привет!',
        'Этот тестовый бот для для проверки категоризации сообщений.',
        'Пришлите мне сообщение для определения категории.'
    ]

    await message.reply('\n'.join(msg))
