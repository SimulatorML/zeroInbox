from typing import Tuple, List
from aiogram.types import Message
from src.models.gpt_classifier import GptClassifier
from database.topic_controller import UserTopicController as db_controller
from database.msg_controller import MsgData, MsgController as msg_controller
from sentence_transformers import SentenceTransformer

class TgController:
    """
    Handles Telegram group chat topics by adding, editing, and deleting topics.
    """
    @staticmethod
    async def add_topic(message: Message, topic_name: str):
        """
        Adds a new topic to a Telegram group chat and stores it in the database.

        Args:
            message (Message): The Telegram message object, containing user and chat IDs.
            topic_name (str): The name of the topic to be added.

        Responds with an error message if the topic already exists or if there are issues in creating or saving the topic.
        """
        user_id = message.from_user.id
        chat_id = message.chat.id
        topic_name = topic_name.strip().lower()

        topic_id = db_controller.get_topic_id(user_id, chat_id, topic_name)

        if topic_id is None:
            await message.answer(f'Ошибка проверки идентификатора темы "{topic_name}"')
            return

        if topic_id != 0 and topic_name != 'unknown':
            await message.answer(f'Тема "{topic_name}" уже существует')
            return

        try:
            topic = await message.bot.create_forum_topic(chat_id=chat_id, name=topic_name)

            if not topic:
                await message.answer(f'Ошибка добавления в чат темы "{topic_name}"')
                return

            db_result = db_controller.add_topic(user_id, chat_id, topic.message_thread_id, topic_name)

            if db_result == 0:
                await message.answer(f"Тема '{topic_name}' успешно создана")
            else:
                await message.answer(f'Ошибка сохранения в БД темы "{topic_name}"')
        except Exception as e:
            await message.answer(f"Ошибка создания новой темы: {str(e)}")

    @staticmethod
    async def edit_topic(message: Message, curr_topic_name: str, new_topic_name: str):
        """
        Edits the name of an existing topic in a Telegram group chat.

        Args:
            message (Message): The Telegram message object.
            curr_topic_name (str): The current name of the topic.
            new_topic_name (str): The new name to replace the current topic name.

        Notifies the user if the topic does not exist, if the new name is already in use, or if there are issues in renaming the topic.
        """
        user_id = message.from_user.id
        chat_id = message.chat.id

        curr_topic_name = curr_topic_name.strip().lower()
        new_topic_name = new_topic_name.strip().lower()

        curr_topic_id = db_controller.get_topic_id(user_id, chat_id, curr_topic_name)

        if curr_topic_id is None:
            await message.answer(f'Ошибка проверки идентификатора темы "{curr_topic_name}"')
            return

        if curr_topic_id == 0:
            await message.answer(f'Тема c наименованием "{curr_topic_name}" не существует')
            return

        new_topic_id = db_controller.get_topic_id(user_id, chat_id, new_topic_name)

        if new_topic_id is None:
            await message.answer(f'Ошибка проверки идентификатора темы "{new_topic_name}"')
            return

        if new_topic_id != 0:
            await message.answer(f'Тема с наименованием "{new_topic_name}" уже существует')
            return

        try:
            edit_result = await message.bot.edit_forum_topic(chat_id=message.chat.id, message_thread_id=curr_topic_id, name=new_topic_name)

            if edit_result:
                save_result = db_controller.edit_topic(user_id, chat_id, curr_topic_id, new_topic_name)

                if save_result == 0:
                    await message.answer(f'Тема "{curr_topic_name}" успешно переименована в "{new_topic_name}"')
                else:
                    await message.answer(f'Ошибка переименование темы "{curr_topic_name}" в БД')
            else:
                await message.answer(f'Ошибка переименование темы "{curr_topic_name}"')
        except Exception as e:
            await message.answer(f"Ошибка переименования темы: {str(e)}")

    @staticmethod
    async def del_topic(message: Message, topic_name: str):
        """
        Deletes a topic from a Telegram group chat and removes it from the database.

        Args:
            message (Message): The Telegram message object.
            topic_name (str): The name of the topic to be deleted.

        Notifies the user if the topic does not exist or if there are issues in deleting the topic.
        """
        user_id = message.from_user.id
        chat_id = message.chat.id
        topic_name = topic_name.strip().lower()

        topic_id = db_controller.get_topic_id(user_id, chat_id, topic_name)

        if topic_id is None:
            await message.answer(f'Ошибка проверки идентификатора темы "{topic_name}"')
            return

        if topic_id == 0:
            await message.answer(f'Темы с наименованием "{topic_name}" не существует')
            return

        try:
            del_result = await message.bot.delete_forum_topic(chat_id=message.chat.id, message_thread_id=topic_id)

            if del_result:
                save_result = db_controller.del_topic(user_id, chat_id, topic_id)

                if save_result == 0:
                    await message.answer(f'Тема "{topic_name}" успешно удалена')
                else:
                    await message.answer(f'Ошибка удаления темы "{topic_name}" в БД')
            else:
                await message.answer(f'Ошибка удаления темы "{topic_name}"')
        except Exception as e:
            await message.answer(f"Ошибка удаления темы: {str(e)}")

    @staticmethod
    async def move_message(message: Message, topic_name: str):
        """
        Moves a message to a specified topic within a Telegram group chat. If the topic does not exist,
        it creates a new topic and adds the message to it. It also handles the deletion of the original message
        after it's successfully moved.

        Args:
            message (Message): The Telegram message object that needs to be moved.
            topic_name (str): The name of the topic to which the message should be moved.

        Responds with error messages if there are issues with topic verification, topic creation, message copying, or message deletion.
        """
        user_id = message.from_user.id
        chat_id = message.chat.id
        message_id = message.message_id
        topic_name = topic_name.strip().lower()

        topic_id = db_controller.get_topic_id(user_id, chat_id, topic_name)

        if topic_id is None:
            await message.answer(f'Ошибка проверки идентификатора темы "{topic_name}"')
            return

        if topic_id == 0:
            try:
                topic = await message.bot.create_forum_topic(chat_id=chat_id, name=topic_name)

                if not topic:
                    await message.answer(f'Ошибка добавления в чат темы "{topic_name}"')
                    return

                topic_id = topic.message_thread_id

                db_result = db_controller.add_topic(user_id, chat_id, topic_id, topic_name)

                if db_result != 0:
                    await message.answer(f'Ошибка сохранения в БД темы "{topic_name}"')
                    return
            except Exception as e:
                await message.answer(f"Ошибка создания новой темы: {str(e)}")
                return

        # copy & delete source message
        try:
            msg = await message.bot.forward_message(chat_id=chat_id, from_chat_id=chat_id, message_thread_id=topic_id, message_id=message_id)

            if msg:
                del_result = await message.bot.delete_message(chat_id=chat_id, message_id=message_id)

                if not del_result:
                    message.answer('Ошибка удаления исходного сообщения')
            else:
                message.answer(f'Ошибка копирования сообщения в тему "{topic_name}"')
        except Exception as e:
            await message.reply(f'Ошибка перемещения сообщения: {str(e)}')

    @staticmethod
    async def classify_message(message: Message, embedder: SentenceTransformer, classifier: GptClassifier) -> Tuple[bool, str]:
        """
        Classifies the content of a message using a SentenceTransformer model for embedding and a GPT classifier
        for determining the category. It also checks if the classified category is valid and exists within the user's
        current topics and saves the classification result.

        Args:
            message (Message): The Telegram message object containing the text to be classified.
            embedder (SentenceTransformer): The SentenceTransformer model used to encode the message text into embeddings.
            classifier (GptClassifier): The GPT-based classifier used to predict the category of the message.

        Returns:
            Tuple[bool, str]: A tuple containing a boolean indicating the success of the classification and the classified category.

        Raises:
            Responds with appropriate error messages if there are issues in encoding, classification, or during database operations.
        """
        user_id = message.from_user.id
        chat_id = message.chat.id
        msg_id = message.message_id
        msg_text=message.text.lower().strip()

        curr_topics = db_controller.get_user_topics(user_id, chat_id)

        if curr_topics is None:
            await message.answer('Ошибка определения списка доступных категорий/топиков')
            return False, ''

        if len(curr_topics) == 0:
            await message.answer('Список доступных категорий/топиков пуст')
            return False, ''

        msg_emb = embedder.model.encode(msg_text)

        classifier.msg_classes = curr_topics

        msgData = MsgData(user_id=user_id, chat_id=chat_id, msg_id=msg_id, msg_text=msg_text)

        responses = await classifier.predict([msgData])

        if not responses:
            await message.answer('Нет ответа от классификатора')
            return False, ''
        else:
            response = responses[0]

        if response['process_status'].lower() == 'ok':
            resultMsgData = response['message']
            resultMsgData.category = response['msg_class']
            resultMsgData.msg_emb = msg_emb
        else:
            await message.answer('Ошибка классификации сообщения')
            return False, ''

        db_topic_id = curr_topics.get(resultMsgData.category, None)

        if not db_topic_id:
            message.answer(f'Не существующая категория сообщений "{resultMsgData.category}"')
            return False, ''
        else:
            resultMsgData.topic_id = db_topic_id

        db_result = msg_controller.save_messages([resultMsgData])

        if db_result != 0:
            message.answer('Ошибка сохранения результата классификации')
            return False, ''

        return True, resultMsgData.category

    @staticmethod
    async def search_messages(message: Message, msg_pattern: str, embedder: SentenceTransformer, top_k: int = 3) -> List[str]:
        """
        Searches for messages that are semantically similar to a given message pattern within the Telegram group chat.
        It uses a SentenceTransformer model to generate embeddings for the pattern and retrieves the top k similar messages
        based on these embeddings.

        Args:
            message (Message): The Telegram message object where the search command was invoked.
            msg_pattern (str): The text pattern to search for similar messages.
            embedder (SentenceTransformer): The SentenceTransformer model used for generating text embeddings.
            top_k (int, optional): The number of top similar messages to retrieve. Defaults to 3.

        Returns:
            List[str]: A list of similar message texts.

        Raises:
            Responds with an error message if there are issues in generating embeddings or retrieving similar messages.
        """
        user_id = message.from_user.id
        chat_id = message.chat.id
        msg_emb = embedder.model.encode(msg_pattern.lower().strip())

        sim_messages = msg_controller.search_sim_messages(user_id, chat_id, msg_emb, top_k)

        if sim_messages is None:
            await message.answer('Ошибка определения похожих сообщений')
            return []

        if len(sim_messages) == 0:
            await message.answer('Список похожих сообщений пуст')
            return []

        return sim_messages