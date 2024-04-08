from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter
from aiogram.filters.command import Command
from src.bot.tg_connector import TgConnector


class AuthorizationState(StatesGroup):
    """
    This class is used to manage the sequence of inputs required from the user
    to complete the authorization process. Each state corresponds to a specific
    piece of information needed for authorization.
    """
    api_id = State()
    api_hash = State()
    phone_number = State()
    phone_code_hash = State()
    conf_code = State()
    conn = State()


router = Router()


@router.message(Command('sign_in'))
async def sign_in(message: Message, state: FSMContext):
    """
    Initiates the user authorization process by asking the user
    to enter their Telegram API credentials.
    """
    if await state.get_data():
        await message.reply('Пользователь уже аутентифицирован')
        await message.answer('Для повторной аутентификации предварительно выполните команду /sign_out')

        return

    msg = [
        r'Для доступа к сохраненным сообщениям, необходимо указать реквизиты для авторизации пользователя\.',
        r'',
        r'Получить доступ к ним можно следующим образом:',
        r'1\. Войдите в Telegram, используя любое приложение',
        r'2\. На странице https://my\.telegram\.org перейдите в раздел "API development tools"',
        r'3\. В этом разделе будут перечислены `api_id` и `api_hash`\.',
    ]

    await message.answer("\n".join(msg), parse_mode="MarkdownV2")
    await state.set_state(AuthorizationState.api_id)
    await message.answer("Введите api_id:")


@router.message(StateFilter(AuthorizationState.api_id))
async def process_api_id(message: Message, state: FSMContext):
    """
    Processes the user's input for `api_id` and updates the state to expect `api_hash` as the next input.
    """
    await state.update_data(api_id=message.text.lower())
    await state.set_state(AuthorizationState.api_hash)
    await message.answer('Введите api_hash:')


@router.message(StateFilter(AuthorizationState.api_hash))
async def process_api_hash(message: Message, state: FSMContext):
    """
    Processes the user's input for `api_hash` and updates the state to expect the phone number as the next input.
    """
    await state.update_data(api_hash=message.text.lower())
    await state.set_state(AuthorizationState.phone_number)
    await message.answer(
        "Введите номер телефона в полном международном формате `+<код страны><номер телефона>`:",
        parse_mode="MarkdownV2",
    )


@router.message(StateFilter(AuthorizationState.phone_number))
async def process_phone_number(message: Message, state: FSMContext):
    """
    Processes the user's phone number input and initiates the connection to the Telegram API.

    The function updates the FSM state with the user's phone number, creates a TgConnector instance,
    and attempts to connect to the Telegram API. If the connection is successful and the user is not
    already authorized, it sends a confirmation code to the user's phone and updates the state to
    wait for the confirmation code. If the user is already authorized, it completes the authentication process.
    """
    await state.update_data(phone_number=message.text.lower())

    user_data = await state.get_data()

    conn = TgConnector(
        api_id = user_data['api_id'],
        api_hash = user_data['api_hash'],
        phone_number = user_data['phone_number']
    )

    result, msg = await conn.connect()

    if result != 0:
        await state.clear()

        err_message = [
            f'<b>Ошибка подключения</b> - {msg}',
            '',
            'Выполните повторно команду /sign_in и введите корректные реквизиты пользователя.'
        ]

        await message.answer('\n'.join(err_message), parse_mode="HTML",)

        return

    if not await conn.session.is_user_authorized():
        result, phone_code_hash, msg = await conn.send_code()

        if result != 0:
            await state.clear()

            err_message = [
                f'<b>Ошибка отправки кода подтверждения</b> - {msg}',
                '',
                'Выполните повторно команду /sign_in и введите корректные реквизиты пользователя.'
            ]

            await message.answer('\n'.join(err_message), parse_mode="HTML",)

            return

        await state.update_data(phone_code_hash=phone_code_hash)
        await message.reply('Введите полученный код подтверждения с префиксом "z", (пример z12345):')
        await state.set_state(AuthorizationState.conf_code)
    else:
        await state.set_state(AuthorizationState.conf_code)
        await state.update_data(conf_code='z12345')
        await state.set_state(AuthorizationState.conn)
        await state.update_data(conn=conn)
        await message.answer('Аутентификация пользователя успешно завершена')


@router.message(StateFilter(AuthorizationState.conf_code))
async def process_conf_code(message: Message, state: FSMContext):
    """
    Processes the user's confirmation code input and completes the authentication process.

    The function updates the FSM state with the user's confirmation code, creates a TgConnector instance,
    and attempts to sign in to the Telegram API using the confirmation code. If the sign-in is successful,
    it completes the authentication process. If not, it prompts the user to re-enter the correct confirmation code.
    """
    await state.update_data(conf_code=message.text.lower())

    user_data = await state.get_data()

    conn = TgConnector(
        api_id = user_data['api_id'],
        api_hash = user_data['api_hash'],
        phone_number = user_data['phone_number']
    )

    result, msg = await conn.connect()

    if result != 0:
        await state.clear()

        err_message = [
            f'<b>Ошибка подключения</b> - {msg}',
            '',
            'Выполните повторно команду /sign_in и введите корректные реквизиты пользователя.'
        ]

        await message.answer('\n'.join(err_message), parse_mode="HTML",)

        return

    if not await conn.session.is_user_authorized():
        result, msg = await conn.sign_in(user_data['phone_code_hash'], user_data['conf_code'])

        if result == 0:
            await state.set_state(AuthorizationState.conn)
            await state.update_data(conn=conn)
        else:
            await state.clear()

            err_message = [
                f'<b>Ошибка авторизации пользователя</b> - {msg}',
                '',
                'Выполните повторно команду /sign_in и введите корректный код подтверждения.'
            ]

            await message.answer('\n'.join(err_message), parse_mode='HTML')

            return

    await message.answer('Аутентификация пользователя успешно завершена')


@router.message(Command('sign_out'))
async def sign_out(message: Message, state: FSMContext):
    """
    Handles the user sign-out process by logging out the user from their
    Telegram session and clearing their session data.
    """
    user_data = await state.get_data()

    if not user_data:
        await message.answer('Пользователь уже де-аутентифицирован')
        return

    try:
        conn = user_data['conn']
        await conn.session.log_out()
        await state.clear()

        await message.answer('Пользователь успешно де-аутентифицирован')
    except Exception as e:
        await message.answer(f'Ошибка де-аутентификации пользователя: {e}')