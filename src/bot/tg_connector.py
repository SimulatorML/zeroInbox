from typing import Tuple, List
from telethon import TelegramClient
from telethon.tl.types import InputMessagesFilterDocument
from telethon.errors import ApiIdInvalidError, PhoneNumberInvalidError, PhoneCodeInvalidError, PhoneCodeExpiredError
from database.controller import MsgData


class TgConnector:
    """
    A client for interacting with Telegram using the Telethon library.

    This class provides methods to connect to Telegram, start a session, and retrieve messages.

    Attributes:
        api_id (str): The API ID obtained from Telegram.
        api_hash (str): The API hash obtained from Telegram.
        phone_number (str): The phone number associated with the Telegram account.
        session (TelegramClient): The Telethon session object.

    Methods:
        connect(): Establishes a connection to the Telegram API.
        send_code(): Sends a code to the user's phone number for authentication.
        sign_in(phone_code_hash, conf_code): Signs in the user using the code sent to their phone number.
        get_messages(limit=None): Retrieves messages from the user's saved messages.

    Example of use:
        conn = TgConnector(api_id='api_id', api_hash='api_hash', phone_number='phone_number')
        result, msg = await conn.connect()

        if result != 0:
            print(f'Error while connecting - {msg}')
            return

        if not await conn.session.is_user_authorized():
            phone_code_hash = await conn.send_code()

            code = input("Enter confirmation code:")

            result, msg = await conn.sign_in(phone_code_hash, code)

            if result != 0:
                print(f'Error while signing in - {msg}')
                return

        result, messages = await conn.get_messages(8)

        if result == 0:
            print('\n'.join(messages))
        else:
            print(f'Error while receiving user messages, error code: {result}')
    """
    def __init__(self, api_id, api_hash, phone_number):
        """
        Initializes the TgConnector with the provided API ID, API hash, and phone number.

        Args:
            api_id (str): The API ID obtained from Telegram.
            api_hash (str): The API hash obtained from Telegram.
            phone_number (str): The phone number associated with the Telegram account.
        """
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone_number = phone_number


    async def connect(self) -> Tuple[int, str]:
        """
        Establishes a connection to the Telegram service.

        Returns:
            Tuple[int, str]: A tuple containing the status code (0 for success, non-zero for error) and the status message.
        """
        try:
            self.session = TelegramClient(f'z_{self.api_hash}', self.api_id, self.api_hash)

            if not self.session.is_connected():
                await self.session.connect()

            return 0, 'OK'
        except ApiIdInvalidError:
            return 1, 'The api_id/api_hash combination is invalid'
        except PhoneNumberInvalidError:
            return 2, 'The phone number is invalid'
        except Exception as e:
            return 3, e.args[0]


    async def send_code(self) -> Tuple[int, str, str]:
        """
        Sends a code to the user's phone number for authentication.

        Returns:
            Tuple[int, str]: A tuple containing the status code (0 for success, non-zero for error),
            the status message and the phone_code_hash.
        """
        try:
            sent_code_instance = await self.session.send_code_request(self.phone_number)
            phone_code_hash = sent_code_instance.phone_code_hash

            return 0, 'OK', phone_code_hash
        except ApiIdInvalidError:
            return 1, '', 'The api_id/api_hash combination is invalid'
        except Exception as e:
            return 2, '', e.args[0]

    async def sign_in(self, phone_code_hash, conf_code) -> Tuple[int, str]:
        """Signs in the user using the code sent to their phone number.

        Args:
            phone_code_hash (str): The phone code hash obtained from the send_code method.
            conf_code (str): The confirmation code received by the user.

        Returns:
            Tuple[int, str]: A tuple containing a status code (0 for success, non-zero for error) and the status message.
        """
        try:
            if not self.session.is_connected():
                await self.session.connect()

            if not await self.session.is_user_authorized():
                await self.session.sign_in(
                    phone=self.phone_number,
                    bot_token=self.api_hash,
                    phone_code_hash=phone_code_hash,
                    code=conf_code
                )

            return 0, 'OK'
        except PhoneCodeInvalidError:
            return 1, 'The phone code entered was invalid'
        except PhoneCodeExpiredError:
            return 2, 'The confirmation code has expired'
        except Exception as e:
            return 3, e.args[0]


    async def get_messages(self, limit = None) -> Tuple[int, List[MsgData]]:
        """
        Retrieves messages from the user's saved messages.

        Args:
            limit (int, optional): The maximum number of messages to retrieve. Defaults to None.

        Returns:
            Tuple[int, List[Tuple]]: A tuple containing a status code and a list of messages.
        """
        result = []

        if not self.session.is_connected():
            return 1, []

        if not await self.session.is_user_authorized():
            return 2, []

        raw_messages = await self.session.get_messages('me', limit, filter=InputMessagesFilterDocument)

        for msg in raw_messages:
            if msg.text.strip():
                data = MsgData(msg_id=msg.id, msg_text=msg.text.strip(), category='')
                result.append(data)

        return 0, result
