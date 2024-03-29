from aiogram import Router
from aiogram.types import Message
from aiogram.filters.command import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    buttons = [
        [
            InlineKeyboardButton(text='Аутентификация', callback_data='authorize'),
            InlineKeyboardButton(text='Выход', callback_data='authorize')
        ],
        [
            InlineKeyboardButton(text='Классификация', callback_data='categorize'),
            InlineKeyboardButton(text='Поиск сообщений', callback_data='search')
        ],
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons, resize_keyboard=True)

    await message.answer('Выберите действие:', reply_markup=keyboard)
