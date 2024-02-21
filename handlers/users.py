import logging

from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from keyboards.main_menu import user_menu, admin_menu
from calendar.calendar import WorkoutCalendar, calendar_callback
from create_bot import bot, db
from constants import ADMIN_IDS


async def cancel_state(state: FSMContext) -> None:
    """
    Cancel the FSMContext machine state.
    :param state:
    :return: None
    """
    current_state = await state.get_state(state)
    if current_state is not None:
        await state.finish()
    else:
        pass


class UserActions(StatesGroup):
    choose_date = State()


async def start_bot(message: Message, state: FSMContext):
    """
    Start the bot and check_
    :param message:
    :param state:
    :return:
    """
    telegram_id = message.from_user.id
    cancel_state(state)
    if telegram_id in ADMIN_IDS:
        await message.answer(
            text='Привет, коллега {message.from_user.first_name}',
            reply_markup=admin_menu
        )
    elif await db.get_user_by_id(telegram_id) is None:
        # add new user to database!
        await message.answer(
            text='Привет! У нас здесь впервые, я помогаю записаться на массаж 😊'
                 'и ответить на интересующие вопросы 😉',
            reply_markup=user_menu
        )
    else:
        await message.answer(
            text='Привет! Рад снова видеть тебя 😎\n\n'
                 'Хочешь записаться на массаж?',
            reply_markup=user_menu
        )


async def show_calendar_for_user(message: Message, state: FSMContext):
    """
    Shows calendar for user to book the massage session.
    :param message:
    :param state:
    :return:
    """
    await cancel_state(state)
    await message.answer(
        text='Выберите дату записи на массаж:\n Слова о маркировке, есть/нет'
             'записи',
        reply_markup=await WorkoutCalendar().start_calendar()
    )
    await state.set_state(UserActions.choose_date)


async def check_active_sessions_for_user(message: Message, state: FSMContext):
    """

    :param message:
    :param state:
    :return:
    """
    await cancel_state(state)
    telegram_id = message.from_user.id
    # GET ACTIVE SESSIONS FOR USER BY ID
    await message.answer(
        text='ТУТ ЗАПИСЬ О МАССАЖЕ',
        # КНОПКА ОТМЕНЫ ЕЛСИ ВРЕМЯ ЕЩЁ ПОЗВОЛЯЕТ
    )


async def ask_about_massage(message: Message, state: FSMContext):
    """

    :param message:
    :param state:
    :return:
    """
    await cancel_state()

