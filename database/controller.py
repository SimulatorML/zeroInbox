from typing import List, Tuple
from src.config import DB_PARAMS
from database.pg_connector import PgConnector


class MsgData:
    """
    Represents a single message with its associated data.

    Attributes:
        msg_id (int): The unique identifier of the message.
        msg_text (str): The text content of the message.
        category (str): The category assigned to the message.
    """
    def __init__(self, msg_id: int, msg_text: str, category: str):
        self.msg_id = msg_id
        self.msg_text = msg_text
        self.category = category


class MsgController:
    """
    Controller class for managing message data in the database.

    Methods:
        _get_unprocessed_messages(user_id, messages): Retrieves unsaved messages for a given user.
        save_messages(user_id, messages): Saves a list of messages to the database.
        get_cat_messages(user_id, category): Retrieves messages for a given user and category.
    """
    @staticmethod
    def _get_unprocessed_messages(user_id: str, messages: List[MsgData]) -> Tuple[int, List[MsgData]]:
        """
        Retrieves a list of unsaved messages for a given user.

        Args:
            user_id (str): The unique identifier of the user.
            messages (List[MsgData]): A list of MsgData objects to check for unsaved messages.

        Returns:
            Tuple[int, List[MsgData]]: A tuple containing a status code and a list of unsaved MsgData objects.
        """
        conn = PgConnector(**DB_PARAMS)

        msg_ids = [str(msg.msg_id) for msg in messages]

        str_msg_ids = ','.join(msg_ids)

        query = '''
            with check_ids as (
	            select unnest(string_to_array(%(ids)s, ','))::int as msg_id
            )
            select coalesce(string_agg(c.msg_id::text, ','), '' ) as msg_ids
            from check_ids c
	            left outer join zib.messages m on m.msg_id=c.msg_id and m.user_id=%(user_id)s
            where m.msg_id is null;
        '''

        params = {
            'ids': str_msg_ids,
            'user_id': user_id
        }

        x, msg, result = conn.get_data(query, params)

        if x != 0:
            return x, []

        if result[0][0] == '':
            return 0, []

        msg_to_cat = list(map(int, result[0][0].split(',')))

        return 0, [msg for msg in messages if msg.msg_id in msg_to_cat]


    @staticmethod
    def save_messages(user_id: str, messages: List[MsgData]) -> int:
        """
        Saves a list of messages to the database for a given user.

        Args:
            user_id (str): The unique identifier of the user.
            messages (List[MsgData]): A list of MsgData objects to be saved.

        Returns:
            int: The number of errors encountered during the save process.
        """
        query = '''
            insert into zib.messages(user_id, msg_id, msg_text, category)
            values(%(user_id)s, %(msg_id)s, %(msg_text)s, %(category)s)
        '''

        conn = PgConnector(**DB_PARAMS)
        err_qty = 0

        for msg in messages:
            params = {
                'user_id': user_id,
                'msg_id': msg.msg_id,
                'msg_text': msg.msg_text,
                'category': msg.category
            }

            result, msg = conn.save_data(query, params)

            if result != 0:
                err_qty += 1

        return err_qty

    @staticmethod
    def get_user_totals(user_id: str) -> Tuple[int, List[Tuple]]:
        """
        Retrieves the total count of messages for each category for a given user.

        Args:
            user_id (str): The unique identifier of the user.

        Returns:
            Tuple[int, List[MsgData]]: A tuple containing a status code and
            a list of tuples, each containing a category (str) and its corresponding message count (int).
        """
        conn = PgConnector(**DB_PARAMS)

        query = '''
            select category, count(1) as qty
            from zib.messages
            where user_id=%(user_id)s
            group by category
            order by qty desc
        '''

        params = {
            'user_id': user_id
        }

        x, msg, totals = conn.get_data(query, params)

        if x != 0:
            return x, []

        result = []
        for tot in totals:
            category, qty = tot
            result.append((category, qty))

        return 0, result


    @staticmethod
    def get_cat_messages(user_id: str, category: str) -> Tuple[int, List[MsgData]]:
        """
        Retrieves messages for a given user and category.

        Args:
            user_id (str): The unique identifier of the user.
            category (str): The category of messages to retrieve.

        Returns:
            Tuple[int, List[MsgData]]: A tuple containing a status code and a list of MsgData objects.
        """
        conn = PgConnector(**DB_PARAMS)

        query = '''
            select msg_id, msg_text
            from zib.messages
            where user_id=%(user_id)s and category=%(category)s
            order by id desc
        '''

        params = {
            'user_id': user_id,
            'category': category
        }

        x, msg, messages = conn.get_data(query, params)

        if x != 0:
            return x, []

        result = []
        for msg in messages:
            msg_id, msg_text = msg
            data = MsgData(msg_id, msg_text, category)
            result.append(data)

        return 0, result
