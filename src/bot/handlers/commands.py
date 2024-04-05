from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import Command, CommandObject
from src.models.gpt_classifier import GptClassifier
from database.controller import MsgController as controller

router = Router()

@router.message(Command('start'))
async def cmd_start(message: Message):
    msg = [
        'Список доступных команд:',
        '/sign_in: Аутентификация пользователя',
        '/classify: Классификация текущих сообщений пользователя',
        '/results: Итоги по категориям сообщений',
        '/search <category>: Поиск сообщений согласно указанной категории',
        '/sign_out: Де-аутентификация пользователя'
    ]

    await message.answer('\n'.join(msg))


@router.message(Command('classify'))
async def classify_messages(message: Message, state: FSMContext, classifier: GptClassifier):
    """
    Classifies user's saved messages and stores the classifications in the database.

    The function first checks if the user is authenticated by looking for user data in the state.
    If the user is not authenticated, it prompts the user to sign in.
    It then proceeds to retrieve and classify the messages, updating the user on the progress and any errors encountered.
    Finally, it saves the classified messages to the database and informs the user of the outcome.

    Note: The function currently has placeholders for a progress bar, which can be implemented for better user experience.
    """
    user_data = await state.get_data()

    if not user_data:
        await message.answer('Необходима аутентификация пользователя - выполните команду /sign_in')
        return

    conn = user_data['conn']

    user_id = user_data['api_hash']

    await message.bot.send_chat_action(message.chat.id, action="typing")

    # TODO: add progress bar for process
    x, messages = await conn.get_messages()

    await message.bot.send_chat_action(message.chat.id, action="typing")

    if x != 0:
        await message.answer('Ошибка чтения сообщений пользователя')
        return

    if len(messages) == 0:
        await message.answer('Список сообщений пользователя пуст')

    x, unprocessed_messages = controller._get_unprocessed_messages(user_id, messages)

    if x != 0:
        await message.answer('Ошибка проверки необработанных сообщений')

    if len(unprocessed_messages) == 0:
        await message.answer('Все сообщения уже классифицированы')
        return

    # TODO: add progress bar for process
    response = await classifier.predict(unprocessed_messages[:4])

    processed_messages = []

    for item in response:
        if item['process_status'].lower() == 'ok':
            data = item['message']
            data.category = item['msg_class']
            processed_messages.append(data)

    if len(processed_messages) == 0:
        await message.answer('Ни одно сообщение не было классифицировано - попробуйте повторить операцию позже')
        return

    if len(unprocessed_messages) != len(processed_messages):
        await message.answer('Не все сообщения были классифицированы, необходим повторный перезапуск команды /classify')

    x = controller.save_messages(user_id, unprocessed_messages)

    msg_qty = len(unprocessed_messages)

    if x == 0:
        await message.answer(f'Все сообщения[{msg_qty}] были успешно классифицированы и сохранены в БД')
    else:
        await message.answer(f'Все сообщения[{msg_qty}] были классифицированы, но [{x}] сообщений НЕ были сохранены в БД')


@router.message(Command('results'))
async def get_class_totals(message: Message, state: FSMContext):
    """
    Retrieves and displays the total number of classified messages for each category for the authenticated user.

    The function first checks if the user is authenticated by looking for user data in the state.
    If the user is not authenticated, it prompts the user to sign in.
    It then retrieves the classification results from the database and formats them into a message, which is sent back to the user.
    If there are no classified messages or if there is an error in retrieving the results, appropriate messages are sent to the user.
    """
    user_data = await state.get_data()

    if not user_data:
        await message.answer('Необходима аутентификация пользователя - выполните команду /sign_in')
        return

    user_id = user_data['api_hash']

    x, results = controller.get_user_totals(user_id)

    if x != 0:
        await message.answer('Ошибка чтения результатов классификации')
        results

    if len(results) == 0:
        await message.answer('Список классифицированных сообщений пользователя пуст')
        return

    msg = [
        '*Итоги по категориям сообщений:*'
    ]

    for r in results:
        category, qty = r
        msg.append(f'`{category}`: {qty} сообщений')

    await message.answer('\n'.join(msg), parse_mode='MarkdownV2')


@router.message(Command('search'))
async def get_cat_messages(message: Message, command: CommandObject, state: FSMContext):
    """
    Retrieves and displays messages belonging to a specific category for the authenticated user.

    The function first checks if the user is authenticated by looking for user data in the state.
    If the user is not authenticated, it prompts the user to sign in.
    It then checks if a category argument was provided with the command. If not, it sends an error message to the user.
    If a category is provided, it retrieves messages from the database belonging to that category and sends them back to the user.
    If there are no messages in the specified category or if there is an error in retrieving the messages, appropriate messages are sent to the user.
    """
    user_data = await state.get_data()

    if not user_data:
        await message.answer('Необходима аутентификация пользователя - выполните команду /sign_in')
        return

    if command.args is None:
        await message.answer('Ошибка: не переданы аргументы команды')
        return

    user_id = user_data['api_hash']
    category = command.args

    x, results = controller.get_cat_messages(user_id, category)

    if x != 0:
        await message.answer('Ошибка чтения сообщений пользователя')
        results

    if len(results) == 0:
        await message.answer(f'Нет сообщений в категории `{category}`')
        return

    for r in results:
        await message.answer(r.msg_text)
