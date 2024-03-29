from typing import Tuple, List
from telethon import TelegramClient
from telethon.errors import ApiIdInvalidError, PhoneNumberInvalidError, PhoneCodeInvalidError
import asyncio


class TelethonClient:
    """
    A client for interacting with Telegram using the Telethon library.

    This class provides methods to connect to Telegram, start a session, and retrieve messages.

    Attributes:
        api_id (str): The API ID obtained from Telegram.
        api_hash (str): The API hash obtained from Telegram.
        phone_number (str): The phone number associated with the Telegram account.
        session (TelegramClient): The Telethon session object.

    Methods:
        first_connect() -> Tuple[int, str]: Connects to Telegram and sends a code request if the user is not authorized.
        start(code: str = '') -> Tuple[int, str]: Starts a session by signing in with the phone number and confirmation code.
        get_messages(limit: int = None) -> Tuple[int, List[str]]: Retrieves a list of messages from the user's saved messages.

    Example of use:
        client = TelethonClient(api_id='api_id', api_hash='api_hash', phone_number='phone_number')

        x, msg = await client.first_connect()

        if x != 0:
            print(msg)
            return

        if not await client.session.is_user_authorized():
            code = input("Enter confirmation code:")
            y, msg = await client.start(code)
        else:
            y, msg = await client.start()

        if y == 0:
            z, result = await client.get_messages(10)
            print(z, result)
        else:
            print(msg)
    """
    def __init__(self, api_id, api_hash, phone_number):
        """
        Initializes the TelethonClient with the provided API ID, API hash, and phone number.

        Args:
            api_id (str): The API ID obtained from Telegram.
            api_hash (str): The API hash obtained from Telegram.
            phone_number (str): The phone number associated with the Telegram account.
        """
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone_number = phone_number
        self.session = TelegramClient(f'zib_{api_hash}', api_id, api_hash)

    async def first_connect(self) -> Tuple[int, str]:
        """
        Connects to Telegram and sends a code request if the user is not authorized.

        This method should be executed first to obtain the confirmation code for authorization.

        Returns:
            Tuple[int, str]: A tuple containing the status code and message.
        """
        try:
            await self.session.connect()

            if not await self.session.is_user_authorized():
                #await self.session.sign_in(self.phone_number)
                await self.session.send_code_request(self.phone_number)

            return 0, 'OK'
        except ApiIdInvalidError:
            return 1, 'ApiIdInvalidError: The api_id/api_hash combination is invalid.'
        except PhoneNumberInvalidError:
            return 2, 'PhoneNumberInvalidError: The phone number is invalid.'
        except Exception as e:
            return 3, e.args[0]

    async def start(self, code = '') -> Tuple[int, str]:
        """
        Starts a session by signing in with the phone number and confirmation code.

        This method should be executed after `first_connect` in case of successful execution.

        Args:
            code (str, optional): The confirmation code received from Telegram. Defaults to ''.

        Returns:
            Tuple[int, str]: A tuple containing the status code and message.
        """
        try:
            if not await self.session.is_user_authorized():
                await self.session.sign_in(phone=self.phone_number, code=code)

            return 0, 'OK'
        except PhoneCodeInvalidError:
            return 1, 'PhoneCodeInvalidError: The phone code entered was invalid.'
        except ConnectionError:
            return 2, 'ConnectionError: Cannot send requests while disconnected.'
        except Exception as e:
            return 3, e.args[0]

    async def get_messages(self, limit = None) -> Tuple[int, List[str]]:
        """
        Retrieves a list of messages from the user's saved messages.

        Args:
            limit (int, optional): The maximum number of messages to retrieve. Defaults to None.

        Returns:
            Tuple[int, List[str]]: A tuple containing the status code and a list of message texts.
        """
        result = []

        if not await self.session.is_user_authorized():
            return 1, []

        raw_messages = await self.session.get_messages('me', limit)

        for msg in raw_messages:
            #date = msg.date.strftime('%Y-%m-%d %H:%M:%S')
            if msg.text.strip():
                result.append(msg.text)

        return 0, result
