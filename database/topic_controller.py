from typing import Dict
from src.config import DB_PARAMS
from database.pg_connector import PgConnector


class UserTopicController:
    """
    A controller class to handle operations related to user-defined topics in a chat application.
    This includes retrieving, adding, editing, and deleting topics associated with a user in a specific chat.
    """
    @staticmethod
    def get_topic_id(user_id: int, chat_id: int, topic_name: str) -> int:
        """
        Retrieves the topic ID based on the user ID, chat ID, and topic name.

        Args:
            user_id (int): The user's identifier.
            chat_id (int): The chat's identifier.
            topic_name (str): The name of the topic.

        Returns:
            int: The topic ID if found, 0 if not found, or None in case of an error.
        """
        conn = PgConnector(**DB_PARAMS)

        query = '''
            select topic_id
            from zib.user_topics
            where user_id=%(user_id)s and chat_id=%(chat_id)s and lower(topic_name)=lower(%(topic_name)s);
        '''

        params = {
            'user_id': user_id,
            'chat_id': chat_id,
            'topic_name': topic_name
        }

        x, _, result = conn.get_data(query, params)

        if x != 0:
            return None

        if result:
            return result[0][0]

        return 0


    @staticmethod
    def get_user_topics(user_id: int, chat_id: int) -> Dict:
        """
        Retrieves all topics associated with a user in a specific chat.

        Args:
            user_id (int): The user's identifier.
            chat_id (int): The chat's identifier.

        Returns:
            Dict: A dictionary mapping topic names to topic IDs, or None in case of an error.
        """
        conn = PgConnector(**DB_PARAMS)

        query = '''
            select topic_id, lower(topic_name) as topic_name
            from zib.user_topics
            where user_id=%(user_id)s and chat_id=%(chat_id)s;
        '''

        params = {
            'user_id': user_id,
            'chat_id': chat_id,
        }

        x, _, result = conn.get_data(query, params)

        topics = {}

        if x != 0:
            return None

        if result:
            for topic_id, topic_name in result:
                topics[topic_name] = topic_id

        return topics

    @staticmethod
    def add_topic(user_id: int, chat_id: int, topic_id: int, topic_name: str) -> int:
        """
        Adds a new topic for a user in a specific chat.

        Args:
            user_id (int): The user's identifier.
            chat_id (int): The chat's identifier.
            topic_id (int): The identifier for the new topic.
            topic_name (str): The name of the new topic.

        Returns:
            int: The result of the insert operation (0 if successful, error code otherwise).
        """
        query = '''
            insert into zib.user_topics(user_id, chat_id, topic_id, topic_name)
            values(%(user_id)s, %(chat_id)s, %(topic_id)s, lower(%(topic_name)s)) on conflict do nothing;
        '''

        conn = PgConnector(**DB_PARAMS)

        params = {
            'user_id': user_id,
            'chat_id': chat_id,
            'topic_id': topic_id,
            'topic_name': topic_name
        }

        result, _ = conn.save_data(query, params)

        return result

    @staticmethod
    def edit_topic(user_id: int, chat_id: int, topic_id: int, new_topic_name: str) -> int:
        """
        Edits the name of an existing topic for a user in a specific chat.

        Args:
            user_id (int): The user's identifier.
            chat_id (int): The chat's identifier.
            topic_id (int): The identifier for the existing topic.
            new_topic_name (str): The new name for the topic.

        Returns:
            int: The result of the update operation (0 if successful, error code otherwise).
        """
        query = '''
            update zib.user_topics
                set topic_name=lower(%(new_topic_name)s)
            where user_id=%(user_id)s and chat_id=%(chat_id)s and topic_id=%(topic_id)s;
        '''

        conn = PgConnector(**DB_PARAMS)

        params = {
            'user_id': user_id,
            'chat_id': chat_id,
            'topic_id': topic_id,
            'new_topic_name': new_topic_name
        }

        result, _ = conn.save_data(query, params)

        return result


    @staticmethod
    def del_topic(user_id: int, chat_id: int, topic_id: int) -> int:
        """
        Deletes a topic and all associated messages for a user in a specific chat.

        Args:
            user_id (int): The user's identifier.
            chat_id (int): The chat's identifier.
            topic_id (int): The identifier of the topic to delete.

        Returns:
            int: The result of the delete operation (0 if successful, error code otherwise).
        """
        query = '''
            delete from zib.user_messages where user_id=%(user_id)s and chat_id=%(chat_id)s and topic_id=%(topic_id)s;
            delete from zib.user_topics where user_id=%(user_id)s and chat_id=%(chat_id)s and topic_id=%(topic_id)s;
        '''

        conn = PgConnector(**DB_PARAMS)

        params = {
            'user_id': user_id,
            'chat_id': chat_id,
            'topic_id': topic_id
        }

        result, _ = conn.save_data(query, params)

        return result

