from aiogram import Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter
from aiogram import F


class AuthorizationState(StatesGroup):
    """
    This class is used to manage the sequence of inputs required from the user
    to complete the authorization process. Each state corresponds to a specific
    piece of information needed for authorization.
    """
    api_id = State()
    api_hash = State()
    phone_number = State()
    conf_code = State()


router = Router()


@router.callback_query(F.data == "authorize")
async def authorize_user(callback: CallbackQuery, state: FSMContext):
    """
    Initiates the user authorization process by asking the user
    to enter their Telegram API credentials.
    """
    await state.clear()

    msg = [
        r"Для доступа к сохраненным сообщениям, необходимо указать реквизиты для авторизации пользователя\.",
        r"",
        r"Получить доступ к ним можно следующим образом:",
        r"1\. Войдите в Telegram, используя любое приложение",
        r'2\. На странице https://my\.telegram\.org перейдите в раздел "API development tools"',
        r"3\. В этом разделе будут перечислены `api_id` и `api_hash`\.",
    ]

    await callback.message.answer("\n".join(msg), parse_mode="MarkdownV2")
    await state.set_state(AuthorizationState.api_id)
    await callback.message.answer("Введите api_id:")


@router.message(StateFilter(AuthorizationState.api_id))
async def process_api_id(message: Message, state: FSMContext):
    """
    Processes the user's input for `api_id` and
    updates the state to expect `api_hash` as the next input.
    """
    await state.update_data(api_id=message.text.lower())
    await state.set_state(AuthorizationState.api_hash)
    await message.answer("Введите api_hash:")


@router.message(StateFilter(AuthorizationState.api_hash))
async def process_api_hash(message: Message, state: FSMContext):
    """
    Processes the user's input for `api_hash` and
    updates the state to expect the phone number as the next input.
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
    Processes the user's input for the phone number and
    updates the state to expect the confirmation code as the next input.
    """
    await state.update_data(phone_number=message.text.lower())
    await message.answer("Authorization complete.")


@router.message(StateFilter(AuthorizationState.conf_code))
async def process_conf_code(message: Message, state: FSMContext):
    """
    Processes the user's input for the confirmation code and
    completes the authorization process.
    """
    await state.update_data(phone_number=message.text.lower())
    await message.answer("Authorization complete.")
