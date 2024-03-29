from aiogram import Router
from aiogram.types import Message

router = Router()

@router.message()
async def echo(message: Message):
    # Your message handling logic here
    await message.answer(message.text)
