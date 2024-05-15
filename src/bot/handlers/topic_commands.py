from sys import argv
from aiogram import Router
from aiogram.types import Message
from aiogram.filters.command import Command, CommandObject
from src.bot.tg_controller import TgController as tg_controller
from sentence_transformers import SentenceTransformer

router = Router()

@router.message(Command('start'))
async def cmd_start(message: Message):
    """Responds to the '/start' command by sending a list of available commands and automatically creating an 'unknown' topic."""
    msg = [
        'Список доступных команд:',
        '/add_topic <topic_name>: Создание новой темы',
        '/edit_topic <current topic name> <new topic name>: Переименование темы',
        '/del_topic <topic_name>: Удаление темы вместе сообщениями',
        '/search <message> <top_k>: Поиск top k семантически близких сообщений согласно указанного шаблона',
    ]

    await tg_controller.add_topic(message, 'unknown')

    await message.answer('\n'.join(msg))


@router.message(Command('add_topic'))
async def create_topic(message: Message, command: CommandObject):
    """
    Handles the '/add_topic' command to create a new topic. It requires a topic name as an argument.

    Args:
        message (Message): The message object from Telegram.
        command (CommandObject): The command object containing arguments.

    Raises:
        Sends an error message if no topic name is provided.
    """
    if command.args is None:
        await message.answer('Ошибка: не указано наименование темы')
        return

    topic_name: str = command.args

    if not topic_name:
        await message.answer("Укажите наименование темы после текста команды.")
        return

    await tg_controller.add_topic(message, topic_name)


@router.message(Command('edit_topic'))
async def rename_topic(message: Message, command: CommandObject):
    """Handles the '/edit_topic' command to rename an existing topic. It requires two arguments: the current topic name and the new topic name.

    Args:
        message (Message): The message object from Telegram.
        command (CommandObject): The command object containing arguments.

    Raises:
        Sends an error message if the required two topic names are not provided."""
    if command.args is None:
        await message.answer('Ошибка: не указано наименование темы')
        return

    cmd_list = command.args.split()

    if len(cmd_list) != 2:
        await message.answer('Ошибка: Укажите 2 параметра темы, разделенные пробелом')

    curr_topic_name = cmd_list[0]
    new_topic_name = cmd_list[1]

    await tg_controller.edit_topic(message, curr_topic_name, new_topic_name)


@router.message(Command('del_topic'))
async def delete_topic(message: Message, command: CommandObject):
    """
    Handles the '/del_topic' command to delete an existing topic and its associated messages. It requires the topic name as an argument.

    Args:
        message (Message): The message object from Telegram.
        command (CommandObject): The command object containing arguments.

    Raises:
        Sends an error message if no topic name is provided.
    """
    if command.args is None:
        await message.answer('Ошибка: не указано наименование темы')
        return

    topic_name: str = command.args

    if not topic_name:
        await message.answer("Укажите наименование темы для удаления.")
        return

    await tg_controller.del_topic(message, topic_name)


@router.message(Command('search'))
async def search_messages(message: Message, command: CommandObject, embedder: SentenceTransformer):
    """
    Handles the '/search' command to find top k semantically similar messages according to a specified pattern. Requires a message pattern and a number 'k' as arguments.

    Args:
        message (Message): The message object from Telegram.
        command (CommandObject): The command object containing arguments.
        embedder (SentenceTransformer): The SentenceTransformer model used for message embedding.

    Raises:
        Sends an error message if the required parameters are not provided correctly.
    """
    if command.args is None:
        await message.answer('Ошибка: не указаны параметры команды')
        return

    cmd_list = command.args.split()

    if len(cmd_list) < 2:
        await message.answer('Ошибка: Укажите 2 параметра, разделенные пробелом')

    msg_patern = " ".join(cmd_list[0:-1])
    top_k = cmd_list[-1]

    results = await tg_controller.search_messages(message, msg_patern, embedder, top_k)

    if results:
        await message.answer('Результаты поиска:')

    for r in results:
        await message.answer(r.msg_text)
