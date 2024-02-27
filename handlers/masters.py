import logging
import datetime

from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from constants import ADMIN_IDS, WEEKDAYS
from create_bot import db
from handlers.users import cancel_state
from keyboards.master_kb import working_time_and_days_inline


class MasterActions(StatesGroup):
    working_day = State()
    working_hours = State()
    days_off = State()

async def check_time_format(work_time: str):
    """

    :param work_time:
    :return:
    """
    try:
        if "," in input:
            times = input.split(", ")
        else:
            times = [input]

        working_hours = []
        for time in times:
            start, end = [int(x) for x in time.split("-")]
            start_time = datetime.time(start)
            end_time = datetime.time(end)
            working_hours.append((start_time, end_time))
    except ValueError or TypeError:
        return False


async def working_time_menu(message: Message, state: FSMContext):
    """
    Show inline keybaord for master to adjust working hours and days.
    :param message:
    :param state:
    :return:
    """
    telegram_id = message.from_user.id
    await cancel_state(state)
    logging.info('Ау')
    if telegram_id in ADMIN_IDS:
        await message.answer(
            'Назначь рабочее время на неделю:',
            reply_markup=await working_time_and_days_inline(telegram_id)
        )
        await state.set_state(MasterActions.working_day)


async def choose_workout_day(query: CallbackQuery, state: FSMContext):
    """
    Choose the workout day to change.
    :param query:
    :param state:
    :return:
    """
    async with state.proxy() as data:
        if query.data == 'days_off':
            await query.message.edit_text(
                'Введи дополнительно даты текущего месяца для выходных:\n\n'
                'Например: 7,11,22'
            )
            await state.set_state(MasterActions.days_off)
        else:
            data['selected_weekday'] = query.data
            for key, value in WEEKDAYS.items():
                if query.data == value:
                    weekday = key
            await query.message.edit_text(
                f'Введи рабочие часы для работы во {weekday}:\n\n'
                f'Вводить в формате: 9-12,13-21\n'
                f'То есть рабочее время 9 до 21 с перерывом с 12 до 13'
            )
            await state.set_state(MasterActions.working_hours)


async def update_working_hours(message: Message, state: FSMContext):
    """

    :param message:
    :param state:
    :return:
    """
    telegram_id = message.from_user.id
    async with state.proxy() as data:
        await db.update_master_worktime(
            telegram_id=telegram_id,
            work_graphic=message.text,
            query_data=data['selected_weekday'],
        )



def register_master_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(
        choose_workout_day,
        lambda query: True,
        state=MasterActions.working_day

    )
    dp.register_message_handler(
        update_working_hours,
        state=MasterActions.working_hours
    )
    dp.register_message_handler(
        working_time_menu,
        text='График работы 📅',
        state='*'
    )
