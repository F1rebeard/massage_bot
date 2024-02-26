from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from constants import MASSAGES, OTHER_SERVICE, EXTRA_SERVICE


def get_service_info(data: dict, unit: [str, int]) -> [str, int, int]:
    service_info = data.get(unit)
    name: str = service_info[0]
    time: int = int(service_info[1])
    price: int = int(service_info[2])
    return name, time, price


def service_inline_keyboard() -> InlineKeyboardMarkup:
    """
    Creates InlineKeyboardMarkup with available service for user to choose.
    :return:
    """
    massages = set(MASSAGES.keys())
    other_service = set(OTHER_SERVICE.keys())
    keyboard = InlineKeyboardMarkup()
    for massage in massages:
        # get the massage info for user
        name, time, price = get_service_info(MASSAGES, massage)
        keyboard.add(
            InlineKeyboardButton(
                text=f'{name}, {time} мин., {price}  руб.',
                callback_data=massage
            )
        )
    for service in other_service:
        name, time, price = get_service_info(OTHER_SERVICE, service)
        keyboard.add(
            InlineKeyboardButton(
                text=f'{name}, {time} мин., {price}  руб.',
                callback_data=service
            )
        )
    keyboard.add(
        InlineKeyboardButton(
            text='Подарочный сертификат 🎁 ',
            callback_data='gift_certificate'
        )
    )
    return keyboard


def extra_service_inline_keyboard() -> InlineKeyboardMarkup:
    """
    Creates InlineKeyboardMarkup with available extra service
    for user to choose.
    :return:
    """
    services = list(EXTRA_SERVICE.keys())
    keyboard = InlineKeyboardMarkup()
    for service in services:
        name, time, price = get_service_info(EXTRA_SERVICE, service)
        keyboard.add(
            InlineKeyboardButton(
                text=f'{name}, {time} мин., {price}  руб.',
                callback_data=service
            )
        )
    keyboard.add(
        InlineKeyboardButton(
            text='Продолжить без доп. услуг',
            callback_data='select_date'
        )
    )
    keyboard.add(
        InlineKeyboardButton(
            text='Назад',
            callback_data='backward'
        )
    )
    return keyboard


extra_service_kb = extra_service_inline_keyboard()




