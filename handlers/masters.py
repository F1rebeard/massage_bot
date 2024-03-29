import logging
import datetime
import re

from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from constants import ADMIN_IDS, WEEKDAYS
from create_bot import db
from massage_calendar.work_graph import (
    get_all_working_hours,
    work_weekday_graphic_for_calendar)
from handlers.users import cancel_state
from keyboards.master_kb import working_time_and_days_inline
from keyboards.main_menu import admin_menu


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
    if telegram_id in ADMIN_IDS:
        await cancel_state(state)
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
                f'То есть рабочее время 9 до 21 с перерывом с 12 до 13, если'
                f'день недели нерабочий - вводим 0'
            )
            await state.set_state(MasterActions.working_hours)
        await query.answer()


async def update_working_hours(message: Message, state: FSMContext):
    """

    :param message:
    :param state:
    :return:
    """
    telegram_id = message.from_user.id
    if not re.match(r"0|\d+-\d+(, \d+-\d+)*", message.text):
        await message.answer(
            'Неправильный формат ввода времени!\n\n'
            'Введи в формате 9-12, 13-20 или 9-21 (без перерыва)',
            reply_markup=admin_menu
        )
        all_working_hours = await get_all_working_hours()
        await message.answer(
            text=f'{await work_weekday_graphic_for_calendar(all_working_hours)}'
        )
    else:
        async with state.proxy() as data:
            await db.update_master_worktime(
                telegram_id=telegram_id,
                work_graphic=message.text,
                query_data=data['selected_weekday'],
            )
        await message.answer(
            'График обновлен!',
            reply_markup=await working_time_and_days_inline(telegram_id)
        )
        await state.set_state(MasterActions.working_day)


async def update_days_off(message: Message, state: FSMContext):
    """

    :param message:
    :param state:
    :return:
    """
    telegram_id = message.from_user.id
    if not re.match(
            r"^(([1-9]|[12][0-9]|3[01]), )+([1-9]|[12][0-9]|3[01])$",
            message.text):
        await message.answer(
            'Неправильный формат ввода даты!\n\n'
            'Введи в формате: 1, 21, 26'
        )
    else:
        await db.update_master_worktime(
            telegram_id=telegram_id,
            work_graphic=message.text,
            query_data='days_off'
        )
        await message.answer(
            'График обновлен!',
            reply_markup=await working_time_and_days_inline(telegram_id)
        )
        await state.set_state(MasterActions.working_day)


def register_master_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(
        choose_workout_day,
        lambda query: True,
        state=MasterActions.working_day
    )
    dp.register_message_handler(
        working_time_menu,
        text='График работы 📅',
        state='*'
    )
    dp.register_message_handler(
        update_working_hours,
        state=MasterActions.working_hours
    )
    dp.register_message_handler(
        update_days_off,
        state=MasterActions.days_off
    )

