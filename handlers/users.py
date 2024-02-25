import logging

from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from keyboards.main_menu import user_menu, admin_menu
from keyboards.user_kb import (
    service_inline_keyboard,
    get_service_info,
    extra_service_inline_keyboard,
    backward_button
)
from calendar.calendar import MassageCalendar, calendar_callback
from create_bot import bot, db
from constants import ADMIN_IDS, MASSAGES, OTHER_SERVICE, EXTRA_SERVICE


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
    choose_service = State()
    gift_certificate = State()


async def start_bot(message: Message, state: FSMContext):
    """
    Start the bot and check_
    :param message:
    :param state:
    :return:
    """
    telegram_id = message.from_user.id
    await cancel_state(state)
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


async def show_all_services(message: Message, state: FSMContext):
    """
    Show up a menu with massage types for user.
    :param message:
    :param state:
    :return:
    """
    await cancel_state(state)
    await message.answer(
        'Выберити интересующую услугу 😊',
        reply_markup=service_inline_keyboard()
    )
    await state.set_state(UserActions.choose_service)


async def choose_service(query: CallbackQuery, state: FSMContext):
    """
    Choose a service by user.
    :param query:
    :param state:
    :return:
    """
    async with state.proxy() as data:
        if query.data == 'gift_certificate':
            data['selected_service'] = 'Подарочный сертификат'
            await query.message.edit_text(
                'Можно приобрести подарочный сертификат 🎁 на любую сумму или'
                'на количество процедур. Напишите пожалуйста, какой сертификат'
                ' вы хотели бы 😉?'
            )
            await state.set_state(UserActions.gift_certificate)
        elif query.data in set(MASSAGES.keys()):
            name, time, price = get_service_info(MASSAGES, query.data)
            basic_text = (f'Вы выбрали {name}, длительностью {time} мин.\n'
                          f'Cтоимость: {price} руб.\n\n')
            if query.data in ('general', 'back_and_legs', 'hands_and_neck'):

                await query.message.edit_text(
                    text=basic_text + f'Так же вы можете выбрать'
                                      f' дополнительные услуги:',
                    reply_markup=extra_service_inline_keyboard()
                )
            elif query.data == '4_hands':
                await query.message.edit_text(
                    text=basic_text + f'для этого массажа требуется доступное '
                                f'время для двух мастеров.'
                                f' ВОЗМОЖНО ПРЕДВАРИТЕЛЬНАЯ СВЯЗЬ C МАССАЖИСТОМ'
                                f' УТОЧНИТЬ БЫ!',
                    reply_markup=await MassageCalendar().start_calendar()
                )
            else:
                await query.message.edit_text(
                    text=basic_text,
                    reply_markup=await MassageCalendar().start_calendar()
                )
        elif query.data in set(OTHER_SERVICE.keys()):
            name, time, price = get_service_info(OTHER_SERVICE, query.data)
            basic_text = (f'Вы выбрали {name}, длительностью {time} мин.\n'
                          f'Cтоимость: {price} руб.\n\n')
            await query.message.edit_text(
                text=basic_text,
                reply_markup=await MassageCalendar().start_calendar()
            )










async def show_calendar_for_user(message: Message, state: FSMContext):
    """
    Shows calendar for user to book the massage session.
    :param message:
    :param state:
    :return:
    """
    await message.answer(
        text='Выберите дату записи на массаж:\n Слова о маркировке, есть/нет'
             'записи',
        reply_markup=await MassageCalendar().start_calendar()
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
    await message.answer(
        'Отвечаю на интересующие вопросы и если нужно '
        'отправляю запрос на обратную связь от мастера с интересующими'
        ' вас вопросами'
    )


def register_user_handlers(dp: Dispatcher):
    dp.register_message_handler(
        start_bot,
        commands=['start',],
        state='*'
    )
    dp.register_message_handler(
        show_all_services,
        text='Записаться на массаж 💆‍♂',
        state='*'
    )