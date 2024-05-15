from aiogram import Router, F
from aiogram.types import Message
from src.models.gpt_classifier import GptClassifier
from src.bot.tg_controller import TgController as tg_controller
from sentence_transformers import SentenceTransformer

router = Router()

@router.message(F.text)
async def handle_new_text_message(message: Message, embedder: SentenceTransformer, classifier: GptClassifier):
    """
    Handles new text messages in a chat. If the message is not a topic message, it classifies the message using
    the provided embedder and classifier, and if successfully classified, moves the message to the appropriate category.
    """
    if not message.is_topic_message:
        result, category = await tg_controller.classify_message(message, embedder, classifier)

        if result:
            await tg_controller.move_message(message, category)


@router.message()
async def handle_new_message(message: Message):
    """
    Handles new messages that are not topic-specific by moving them based on their content type.
    This is used for non-text messages like images, audio, etc.
    """
    if not message.is_topic_message:
        await tg_controller.move_message(message, message.content_type)
