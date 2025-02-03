from datetime import datetime
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import BotCommand, Message
from bot.functions import make_reply_button, make_back_button, save_comment, LanguageStates, make_language_button, \
    ChatStates, make_stop_button
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __
from database import insert_user, insert_chat, get_all_chats, change_status, delete_chats
from database.session import get_db_session
from bot.functions import UserStates
import random


main = Router()


@main.message(Command('start'))
async def start_handler(message: Message, state: FSMContext):
    await message.bot.set_my_commands([BotCommand(command="/start", description="Start")])
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    joined_date = datetime.now()

    session = await get_db_session()
    user = await insert_user(session, user_id, username, first_name, last_name, joined_date)
    await session.close()
    main_menu = [
        _("💫 Start chat"),
        _("💬 Comments and Offers"),
        _("ℹ️ About bot"),
        _("🌐 Language 🇺🇸/🇺🇿/🇷🇺")
    ]

    adjust = [1, 2, 1]
    keyboard = await make_reply_button(main_menu, adjust)
    await message.answer(_("Welcome to Anonymous chat bot!"), reply_markup=keyboard)
    await state.update_data(user_id=user_id)

@main.message(F.text == __("💫 Start chat"))
async def chat_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    session = await get_db_session()
    user = await insert_chat(session, user_id)
    await session.close()

    await state.update_data(user_id=user_id)
    await state.set_state(ChatStates.waiting_for_partner)
    keyboard = await make_stop_button()
    await message.answer(_("Waiting for a partner..."), reply_markup=keyboard)


@main.message(ChatStates.waiting_for_partner, F.text != __("🛑 Stop chat"))
async def partner_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    session = await get_db_session()
    try:
        users = await get_all_chats(session)
        if not users:
            await message.answer(_("Unfortunately, there are no other chats to connect 😕"))
            locale = data.get('locale')
            user_id = message.from_user.id
            await state.clear()
            await state.update_data(user_id=user_id, locale=locale)
            main_menu = [
                _("💫 Start chat"),
                _("💬 Comments and Offers"),
                _("ℹ️ About bot"),
                _("🌐 Language 🇺🇸/🇺🇿/🇷🇺")
            ]
            adjust = [1, 2, 1]
            keyboard = await make_reply_button(main_menu, adjust)
            await message.answer(_("Welcome Back to Anonymous chat bot!"), reply_markup=keyboard)
            return

        # Filter users that are available and have active status
        available_users = [user.telegram_id for user in users if user.status]
        if not available_users:
            await message.answer(_("No one is available for a chat right now. Please try again later."))
            return

        random_user_id = random.choice(available_users)
        await state.update_data(random=random_user_id)
        await state.set_state(ChatStates.waiting_for_text)
    finally:
        await session.close()


@main.message(ChatStates.waiting_for_text, F.text != __("🛑 Stop chat"))
async def text_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    user_id = data.get('user_id')
    random_user_id = data.get('random')

    session = await get_db_session()
    try:
        # Change status to indicate both users are in chat
        await change_status(session, user_id)
        await change_status(session, random_user_id)
    finally:
        await session.close()

    await message.answer(_("Please, type your message here..."))
    await state.set_state(ChatStates.waiting_for_message)


@main.message(ChatStates.waiting_for_message)
async def message_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    random_user_id = data.get('random')
    user_message = message.text

    try:
        await message.bot.send_message(random_user_id, user_message)
    except Exception as e:
        # Handle any potential errors when sending a message
        await message.answer(_("Failed to send your message. Please try again later."))
        return


@main.message(ChatStates.waiting_for_partner, F.text == __("🛑 Stop chat"))
@main.message(ChatStates.waiting_for_text, F.text == __("🛑 Stop chat"))
@main.message(ChatStates.waiting_for_message, F.text == __("🛑 Stop chat"))
async def stop_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    user_id = data.get('user_id')
    random_user_id = data.get('random')
    locale = data.get('locale')
    session = await get_db_session()
    await delete_chats(session, user_id)
    await delete_chats(session, random_user_id)
    await session.close()

    await state.clear()
    await state.update_data(user_id=user_id, locale=locale)

    main_menu = [
        _("💫 Start chat"),
        _("💬 Comments and Offers"),
        _("ℹ️ About bot"),
        _("🌐 Language 🇺🇸/🇺🇿/🇷🇺")
    ]

    adjust = [1, 2, 1]
    keyboard = await make_reply_button(main_menu, adjust)
    await message.answer(_("Welcome back to the Main Menu 🏠"), reply_markup=keyboard)

@main.message(F.text == __("ℹ️ About bot"))
async def about_handler(message: Message):
    text = _("1️⃣.This bot is created to help people chat with each other anonymously 💭\n\n" 
             "2️⃣.This bot keeps all information about user secret 👤\n\n"
             "3️⃣.Please, do not use any offensive or curse words while chatting! 🤬\n\n"
             "4️⃣.If you break the rules, your account will be banned permanently 🚫\n\n"
             "5️⃣.Happy chatting 🥂")
    await message.answer(text=text)

@main.message(F.text == __("💬 Comments and Offers"))
async def comment_handler(message: Message, state: FSMContext):
    back_button = await make_back_button()
    await message.answer(
        _("Please type your comment below 💬. Press 'Back ◀️' to go to the main menu."),
        reply_markup=back_button
    )
    await state.set_state(UserStates.waiting_for_comment)

@main.message(UserStates.waiting_for_comment, F.text != __("Back ◀️"))
async def receive_comment(message: Message):
    user_info = message.from_user
    comment = message.text
    await save_comment(user_info, comment)
    await message.answer(_("Thank you for your comment 💬! Feel free to add another one 😁."))

@main.message(UserStates.waiting_for_comment, F.text == __("Back ◀️"))
async def back_handler(message: Message, state: FSMContext):
    main_menu = [
        _("💫 Start chat"),
        _("💬 Comments and Offers"),
        _("ℹ️ About bot"),
        _("🌐 Language 🇺🇸/🇺🇿/🇷🇺")
    ]

    adjust = [1, 2, 1]

    keyboard = await make_reply_button(main_menu, adjust)
    await message.answer(_("Welcome back to the Main Menu 🏠"), reply_markup=keyboard)
    data = await state.get_data()
    code = data.get('locale')
    await state.clear()
    await state.update_data(user_id=message.from_user.id, locale=code)

@main.message(F.text == __("🌐 Language 🇺🇸/🇺🇿/🇷🇺"))
async def language_handler(message: Message, state: FSMContext):
    keyboard = await make_language_button()
    await state.set_state(LanguageStates.language)
    await message.answer(_("Choose the preferred language"), reply_markup=keyboard)

@main.message(LanguageStates.language, F.text != __("Back 🔙"))
async def change_language_handler(message: Message, state: FSMContext, i18n):
    lang = {
        "🇺🇸 English": "en",
        "🇷🇺 Русский": "ru",
        "🇺🇿 O'zbekcha": "uz",
    }
    code = lang.get(message.text.strip())

    if code:
        data = await state.get_data()
        user_id = data.get('user_id', message.from_user.id)

        await state.update_data(locale=code)

        i18n.current_locale = code

        retained_data = {
            'user_id': user_id,
            'locale': code
        }
        await state.clear()
        await state.update_data(**retained_data)
        main_menu = [
            _("💫 Start chat"),
            _("💬 Comments and Offers"),
            _("ℹ️ About bot"),
            _("🌐 Language 🇺🇸/🇺🇿/🇷🇺")
        ]

        adjust = [1, 2, 1]
        keyboard = await make_reply_button(main_menu, adjust)
        await message.answer(_("Language has been changed 😀"), reply_markup=keyboard)
    else:
        await message.answer(_("Invalid language selection. Please choose a valid language."))

@main.message(LanguageStates.language, F.text == __("Back 🔙"))
async def back_handler(message: Message, state: FSMContext):
    main_menu = [
        _("💫 Start chat"),
        _("💬 Comments and Offers"),
        _("ℹ️ About bot"),
        _("🌐 Language 🇺🇸/🇺🇿/🇷🇺")
    ]

    adjust = [1, 2, 1]
    keyboard = await make_reply_button(main_menu, adjust)
    await message.answer(_("Welcome back to the Main Menu 🏠"), reply_markup=keyboard)
    data = await state.get_data()
    code = data.get('locale')
    await state.clear()
    await state.update_data(user_id=message.from_user.id, locale=code)