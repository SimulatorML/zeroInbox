from aiogram import Router, F
from aiogram.types import Message

router = Router()

@router.message(F.text)
async def message_text(message: Message, classifier):
    """Responds to text messages."""
    response = await classifier.predict([message.text])
    msg_class = response[0]['msg_class']

    if msg_class:
        await message.answer(msg_class)
    else:
        await message.answer("Can't categorize the message.")

@router.message()
async def message_others(message: Message):
    """Responds to messages other than text messages."""
    await message.answer(message.content_type)
