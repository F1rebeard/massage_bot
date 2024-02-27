import logging

from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from constants import ADMIN_IDS


class MasterActions(StatesGroup):
    working_hours = State()




async def working_time_menu(message: Message, state: FSMContext):
    """
    Show inline keybaord for master to adjust working hours and days.
    :param message:
    :param state:
    :return:
    """
    await message.answer(
        'Назначь рабочее время на неделю:'
    )
