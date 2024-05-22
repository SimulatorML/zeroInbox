from typing import List
from aiogram import Router, F, types
from aiogram.types import Message
from aiogram_media_group import media_group_handler
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


@router.message(F.media_group_id, F.content_type.in_({'photo'}))
@media_group_handler
async def handle_new_media_group_message(messages: List[types.Message], embedder: SentenceTransformer, classifier: GptClassifier):
    """
    Handles new text messages containing photo media group in a chat.
    If the message is not a topic message, it classifies the message using the provided embedder and classifier,
    and if successfully classified, moves the message to the appropriate category.
    If there is no caption or text, the message is assumed to have 'photo' category.
    """
    if not messages[0].is_topic_message:
        if not (messages[0].caption or messages[0].text):
            await tg_controller.move_media_group_message(messages, messages[0].content_type)
            return
        else:
            result, category = await tg_controller.classify_message(messages[0], embedder, classifier)

        if result:
            await tg_controller.move_media_group_message(messages, category)


@router.message(F.content_type.in_({'photo', 'video', 'document'}))
async def handle_new_photo_message(message: Message, embedder: SentenceTransformer, classifier: GptClassifier):
    """
    Handles new messages containing photo, video or document (not media groups) in a chat.
    If the message is not a topic message, it classifies the message using the provided embedder and classifier,
    and if successfully classified, moves the message to the appropriate category.
    If there is no caption or text, the message is assumed to have category corresponding to the content type.
    """
    if not message.is_topic_message:
        if not (message.caption or message.text):
            await tg_controller.move_message(message, message.content_type)
            return
        else:
            result, category = await tg_controller.classify_message(message, embedder, classifier)

        if result:
            await tg_controller.move_message(message, category)
