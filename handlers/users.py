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
    extra_service_kb
)
from massage_calendar.massage_calendar import MassageCalendar, calendar_callback
from create_bot import bot, db
from constants import ADMIN_IDS, MASSAGES, OTHER_SERVICE, EXTRA_SERVICE


class UserActions(StatesGroup):
    choose_date = State()
    choose_service = State()
    choose_extra = State()
    gift_certificate = State()


async def cancel_state(state: FSMContext) -> None:
    """
    Cancel the FSMContext machine state.
    :param state:
    :return: None
    """
    current_state = await state.get_state()
    if current_state is None:
        pass
    else:
        await state.finish()


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
            text=f'Привет, коллега {message.from_user.first_name}',
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
                ' вы хотели бы 😉?',
            )
            await state.set_state(UserActions.gift_certificate)
        elif query.data in set(MASSAGES.keys()):
            name, time, price = get_service_info(MASSAGES, query.data)
            basic_text = (f'Вы выбрали {name}\nДлительность: {time} мин.\n'
                          f'Стоимость: {price} руб.\n\n')
            if query.data in ('general', 'back_and_legs', 'hands_and_neck'):
                await query.message.edit_text(
                    text=basic_text + f'Так же вы можете выбрать'
                                      f'до 2 дополнительных услуг:',
                    reply_markup=extra_service_inline_keyboard()
                )
                await state.set_state(UserActions.choose_extra)
            elif query.data == '4_hands':
                await query.message.edit_text(
                    text=basic_text + f'для этого массажа требуется доступное '
                                f'время для двух мастеров.'
                                f' ВОЗМОЖНО ПРЕДВАРИТЕЛЬНАЯ СВЯЗЬ C МАССАЖИСТОМ'
                                f' УТОЧНИТЬ БЫ!',
                    reply_markup=await MassageCalendar().start_calendar()
                )
                await state.set_state(UserActions.choose_date)
            else:
                await query.message.edit_text(
                    text=basic_text,
                    reply_markup=await MassageCalendar().start_calendar()
                )
                await state.set_state(UserActions.choose_date)
            # Adding data to memory
            data['selected_service']: str = name
            data['primary_price'] = int(price)
            data['service_time'] = int(time)
        elif query.data in set(OTHER_SERVICE.keys()):
            name, time, price = get_service_info(OTHER_SERVICE, query.data)
            basic_text = (f'Вы выбрали {name}\nДлительность: {time} мин.\n'
                          f'Стоимость: {price} руб.\n\n')
            await query.message.edit_text(
                text=basic_text,
                reply_markup=await MassageCalendar().start_calendar()
            )
            data['selected_service']: str = name
            data['primary_price'] = int(price)
            data['service_time'] = int(time)


async def choose_extra_service(query: CallbackQuery, state: FSMContext):
    """
    Choose extra service as optional
    :param query:
    :param state:
    :return:
    """
    async with state.proxy() as data:
        if query.data == 'backward':
            await state.set_state(UserActions.choose_service)
            await query.message.edit_text(
                text='Выберити интересующую услугу 😊',
                reply_markup=service_inline_keyboard()
            )
        if query.data == 'select_date':
            await query.message.edit_reply_markup(
                reply_markup=await MassageCalendar().start_calendar()
            )
            await state.set_state(UserActions.choose_date)
        if query.data in set(EXTRA_SERVICE.keys()):
            extra_services = data.get('extra_services', [])
            service_names = ''
            total_price: int = data['primary_price']
            total_time: int = data['service_time']
            for button in extra_service_kb.inline_keyboard:
                if button[0].callback_data == query.data:
                    if '❤️' in button[0].text:
                        button[0].text = button[0].text.replace(' ❤️', '')
                    else:
                        button[0].text += ' ❤️'
                    service = query.data
                    if service not in extra_services:
                        extra_services.append(service)
                    else:
                        extra_services.remove(service)
                    await query.message.edit_reply_markup(
                        extra_service_kb)
                    await query.answer()
            data['extra_services'] = extra_services
            logging.info(f'Выбранные доп.сервисы: {extra_services}')
            for extra in extra_services:
                name, time, price = get_service_info(EXTRA_SERVICE, extra)
                service_names += f'- {name}\n'
                total_price += price
                total_time += time
            await query.message.edit_text(
                text=f'Вы выбрали: {data["selected_service"]}\n\n'
                     f'С дополнительными услугами:\n{service_names}\n'
                     f'Длительность: {total_time} мин.\n'
                     f'Стоимость: {total_price} руб.\n',
                reply_markup=extra_service_kb
            )
            if len(data['extra_services']) == 2:
                await query.message.edit_text(
                    text=f'Вы выбрали: {data["selected_service"]}\n\n'
                         f'С дополнительными услугами:\n{service_names}\n'
                         f'Длительность: {total_time} мин.\n'
                         f'Стоимость: {total_price} руб.\n\n'
                         f'А теперь выберите дату сеанса 😊',
                    reply_markup=await MassageCalendar().start_calendar()
                )
                await query.answer()
                await state.set_state(UserActions.choose_date)


# async def choose_gift_certificate():


async def show_calendar_for_user(message: Message, state: FSMContext):
    """
    Shows massage_calendar for user to book the massage session.
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
    dp.register_callback_query_handler(
        choose_service,
        lambda query: True,
        state=UserActions.choose_service
    )
    dp.register_callback_query_handler(
        choose_extra_service,
        lambda query: True,
        state=UserActions.choose_extra
    )
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