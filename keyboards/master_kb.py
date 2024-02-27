from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from create_bot import db


async def working_time_and_days_inline(
        telegram_id: int) -> InlineKeyboardMarkup:
    """

    :param telegram_id:
    :return:
    """
    workout_graphic = await db.get_workout_graphic(telegram_id)
    week_graphic = {
        'Понедельник': (workout_graphic[0], 'monday'),
        'Вторник': (workout_graphic[1], 'tuesday'),
        'Cреда': (workout_graphic[2], 'wednesday'),
        'Четверг': (workout_graphic[3], 'thursday'),
        'Пятница': (workout_graphic[4], 'friday'),
        'Cуббота': (workout_graphic[5], 'saturday'),
        'Воскресенье': (workout_graphic[6], 'sunday')
    }
    keyboard = InlineKeyboardMarkup(row_width=2)
    for weekday, graphic in week_graphic.values():
        keyboard.row()
        keyboard.insert(
            InlineKeyboardButton(text=weekday, callback_data=graphic[1])
        )
        keyboard.insert(
            InlineKeyboardButton(text=graphic[0], callback_data=graphic[1])
        )
    keyboard.row()
    keyboard.insert(
        InlineKeyboardButton(text='Выходные дни', callback_data='days_off')
    )
    keyboard.insert(
        InlineKeyboardButton(text=workout_graphic[7], callback_data='days_off')
    )
    return keyboard

