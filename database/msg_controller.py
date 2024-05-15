from typing import List
from src.config import DB_PARAMS
from database.pg_connector import PgConnector
from psycopg2.extensions import AsIs
import numpy as np


class MsgData:
    """
    A class to represent message data within a chat application.

    Attributes:
        user_id (int): Unique identifier for the user.
        chat_id (int): Unique identifier for the chat.
        topic_id (int): Identifier for the topic within the chat; defaults to 0.
        msg_id (int): Unique identifier for the message.
        msg_text (str): Text content of the message.
        msg_emb (np.ndarray): Embedding vector of the message, initially empty.
        category (str): Category of the message, initially 'unknown'.
    """
    def __init__(self, user_id: int, chat_id: int, msg_id: int, msg_text: str):
        self.user_id = user_id
        self.chat_id = chat_id
        self.topic_id = 0
        self.msg_id = msg_id
        self.msg_text = msg_text
        self.msg_emb = np.empty(0)
        self.category = 'unknown'


class MsgController:
    """
    A controller class to handle message data operations such as searching for similar messages and saving messages to a database.
    """
    @staticmethod
    def search_sim_messages(user_id: int, chat_id: int, msg_emb: np.ndarray, top_k: int = 3) -> List[MsgData]:
        """
        Searches for similar messages based on embedding similarity.

        Args:
            user_id (int): The user's identifier.
            chat_id (int): The chat's identifier.
            msg_emb (np.ndarray): The embedding vector of the message to compare against.
            top_k (int): The number of top similar messages to retrieve.

        Returns:
            List[MsgData]: A list of MsgData instances representing the top_k similar messages.
        """
        conn = PgConnector(**DB_PARAMS)

        query = '''
            select msg_id, msg_text, 1 - (msg_emb <=> '%(msg_emb)s') as cos_sim
            from zib.user_messages
            where user_id=%(user_id)s and chat_id=%(chat_id)s
            order by cos_sim desc
            limit %(top_k)s;
        '''

        params = {
            'user_id': user_id,
            'chat_id': chat_id,
            'msg_emb': AsIs(msg_emb.tolist()),
            'top_k': top_k
        }

        x, _, result = conn.get_data(query, params)

        if x != 0:
            return None

        messages = []

        for msg_id, msg_text, _ in result:
            data = MsgData(user_id, chat_id, msg_id, msg_text)
            messages.append(data)

        return messages


    @staticmethod
    def save_messages(messages: List[MsgData]) -> int:
        """
        Saves a list of message objects to the database.

        Args:
            messages (List[MsgData]): List of MsgData objects to be saved.

        Returns:
            int: Number of messages that failed to be saved.
        """
        query = '''
            insert into zib.user_messages (msg_id, user_id, chat_id, topic_id, msg_text, msg_emb)
            values(%(msg_id)s, %(user_id)s, %(chat_id)s, %(topic_id)s, %(msg_text)s, %(msg_emb)s)
            on conflict do nothing;
        '''

        conn = PgConnector(**DB_PARAMS)
        err_qty = 0

        for msg in messages:
            params = {
                'msg_id': msg.msg_id,
                'user_id': msg.user_id,
                'chat_id': msg.chat_id,
                'topic_id': msg.topic_id,
                'msg_text': msg.msg_text,
                'msg_emb': msg.msg_emb.tolist()
            }

            result, msg = conn.save_data(query, params)

            if result != 0:
                err_qty += 1

        return err_qty
