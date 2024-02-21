import calendar
from datetime import datetime, timedelta

from aiogram import Dispatcher
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from aiogram.utils.callback_data import CallbackData
from aiogram.types import CallbackQuery, Message
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from create_bot import db, bot
from constants import RUS_MONTHS


calendar_callback = CallbackData(
    'workout_calendar', 'act', 'year', 'month', 'day'
)


class WorkoutCalendar:
    async def start_calendar(
            self,
            year: int = datetime.now().year,
            month: int = datetime.now().month,
    ) -> InlineKeyboardMarkup:
        """
        Creates inline keyboard with the provided year and month.
        :param telegram_id
        :param int year: Year to use, if None the current years is used,
        :param int month: Year to use, if None the current month is used.
        :return:
        """
        inline_kb = InlineKeyboardMarkup(row_width=7)
        # for buttons with no answer
        ignore_callback = calendar_callback.new("IGNORE", year, month, 0)
        # First row - Month and Year
        inline_kb.row()
        inline_kb.insert(
            InlineKeyboardButton(
                f'{RUS_MONTHS[month]} {str(year)}',
                callback_data=ignore_callback
            )
        )

        inline_kb.row()
        for day in ["Пн", "Вт", "Cр", "Чт", "Пт", "Cб", "Вс"]:
            inline_kb.insert(
                InlineKeyboardButton(
                    day,
                    callback_data=ignore_callback)
            )

        # Days rows - Days of Month
        month_calendar = calendar.monthcalendar(year, month)
        for week in month_calendar:
            inline_kb.row()
            for day in week:
                if day == 0:
                    inline_kb.insert(
                        InlineKeyboardButton(" ",
                                             callback_data=ignore_callback)
                    )
                    continue
                if (day == datetime.now().day) and (
                        month == datetime.now().month):
                    inline_kb.insert(
                        InlineKeyboardButton(
                            text=f'[{day}]',
                            callback_data=calendar_callback.new(
                                "DAY", year, month, day
                            )
                        )
                    )
                    continue
                inline_kb.insert(
                    InlineKeyboardButton(
                        str(day),
                        callback_data=calendar_callback.new(
                            "DAY", year, month, day)
                    ))
        # Last Row - Buttons
        inline_kb.row()
        inline_kb.insert(
            InlineKeyboardButton(
                "Пред. месяц",
                callback_data=calendar_callback.new(
                    "PREV-MONTH", year, month, day
                )
            )
        )
        inline_kb.insert(
            InlineKeyboardButton(
                text=f' ',
                callback_data=ignore_callback
            )
        )
        inline_kb.insert(
            InlineKeyboardButton(
                "След. месяц",
                callback_data=calendar_callback.new(
                    "NEXT-MONTH", year, month, day
                )
            )
        )
        return inline_kb

    async def chosen_day(self,
                         year: int = datetime.now().year,
                         month: int = datetime.now().month,
                         ) -> InlineKeyboardMarkup:
        inline_kb = InlineKeyboardMarkup(row_width=1)
        inline_kb.add(
            InlineKeyboardButton(
                'Получить задание 🏋️‍',
                callback_data=calendar_callback.new(
                    "GET_WORKOUT", year, month, 0)
            ),
            InlineKeyboardButton(
                'Записать результат ✏️',
                callback_data=calendar_callback.new(
                    "EDIT_RESULTS", year, month, 0)
            ),
            InlineKeyboardButton(
                'Посмотреть результаты  ️🕵️‍♂',
                callback_data=calendar_callback.new(
                    "VIEW_RESULTS", year, month, 0)
            )
        )
        return inline_kb

    async def process_selection(
            self,
            query: CallbackQuery,
            data: CallbackData
    ) -> tuple:
        """
        Process the callback_query. This method generates a new calendar if
        forward or backward is pressed. This method should be called inside
         a CallbackQueryHandler.
        :param query: callback_query, as provided by the CallbackQueryHandler
        :param data: callback_data, dictionary, set by calendar_callback
        :return: Returns a tuple (Boolean,datetime), indicating if a date
         is selected and returning the date if so.
        """
        return_data = (False, None)
        temp_date = datetime(int(data['year']), int(data['month']), 1)
        # empty buttons in calendar, no actions
        if data['act'] == "IGNORE":
            await query.answer(cache_time=60)
        if data['act'] == "PREV-MONTH":
            prev_date = temp_date - timedelta(days=1)
            await query.message.edit_reply_markup(
                await self.start_calendar(
                    telegram_id=query.from_user.id,
                    year=int(prev_date.year),
                    month=int(prev_date.month)))
        if data['act'] == "NEXT-MONTH":
            next_date = temp_date + timedelta(days=31)
            await query.message.edit_reply_markup(
                await self.start_calendar(
                    telegram_id=query.from_user.id,
                    year=int(next_date.year),
                    month=int(next_date.month)))
        if data['act'] == "DAY":
            return_data = True, datetime(
                int(data['year']),
                int(data['month']),
                int(data['day'])
            )
            await query.answer()
        return return_data

    async def day_action(
            self,
            query: CallbackQuery,
            data: CallbackData,
            state: FSMContext
    ) -> None:
        """
        Actions of inline keyboard after choosing the workout_data
        :param query: callback_query
        :param data: commands for inline buttons
        :param state: states for editing and view results
        :return:
        """
        telegram_id = query.from_user.id
        chosen_date = await db.get_chosen_date(telegram_id)
        user_level = await db.get_user_level(telegram_id)
        if data['act'] == "GET_WORKOUT":
            if telegram_id in ADMIN_IDS:
                await state.set_state(ChosenDateData.for_admin)
                await bot.send_message(
                    text='Выбери для какого уровня посмотреть тренировку:',
                    chat_id=telegram_id,
                    reply_markup=choose_kb
                )
            else:
                workout_hashtag = await create_hashtag(telegram_id)
                if user_level == 'Старт':
                    first_day = await first_day_for_start(telegram_id)
                    chosen_date = datetime.strptime(
                        chosen_date, '%Y-%m-%d').date()
                    workout_day = (chosen_date - first_day).days
                    chosen_workout = await db.get_start_workout_for_user(
                        workout_day=workout_day
                    )
                else:
                    chosen_workout = await db.get_workout_for_user(
                        chosen_date,
                        telegram_id
                    )
                chosen_warm_up = await choosing_warm_up_protocol(chosen_workout)
                await query.message.answer(text=chosen_warm_up,
                                           parse_mode=ParseMode.HTML,
                                           protect_content=True)
                await query.message.answer(text=chosen_workout,
                                           protect_content=True)
                await query.message.answer(text=f'Хэштег этой тренировки, чтобы'
                                                f' поделиться результатом'
                                                f' в чатике\n\n'
                                                f'{workout_hashtag}',
                                           )
                await query.answer()
        elif data['act'] == "EDIT_RESULTS":
            workout_hashtag = await create_hashtag(telegram_id)
            exists, workout_result = await db.check_and_return_workout_result(
                telegram_id, workout_hashtag
            )
            if not exists:
                await query.message.answer(text='Введи результат тренировки,'
                                                ' как в чате "Прогресса"\n\n'
                                                'Хэштег вводить не нужно!')
                await state.set_state(ChosenDateData.edit_result)
            else:
                await query.message.answer(
                    text='Уже есть результат за эту тренировку!'
                )
                await query.message.answer(
                    text=f'Вот твой результат: \n\n'
                         f'{workout_hashtag}\n\n{workout_result}'
                )
                await query.answer()
        elif data['act'] == "VIEW_RESULTS":
            workout_hashtag = await create_hashtag(telegram_id)
            workout_results = await db.get_workout_result_by_hashtag(
                workout_hashtag
            )
            await query.message.answer(
                'Результаты других атлетов:'
            )
            for result in workout_results:
                await query.message.answer(
                    f'@{result[0]}\n{result[1]} {result[2]}\n\n{result[3]}'
                )
            await query.message.answer(
                'Это был заключительный результат'
            )
        await query.answer()


async def add_workout_results(
        message: Message,
        state: FSMContext
):
    """
    Adds workout results by user for selected workout
    into workout_history_table.
    :param message:
    :param state:
    :return:
    """
    telegram_id = message.from_user.id
    workout_date = await db.get_chosen_date(telegram_id)
    workout_hashtag = await create_hashtag(telegram_id)
    async with state.proxy() as data:
        data['telegram_id'] = int(telegram_id)
        data['results'] = message.text
        data['hashtag'] = workout_hashtag
    await db.add_workout_result(state)
    await message.answer(f'Результат тренировки добавлен! \n\n'
                         f'Хэштег - {workout_hashtag}\n'
                         f'Дата - {workout_date}')
    await state.finish()


def register_workout_handelrs(dp: Dispatcher):

    dp.register_message_handler(add_workout_results,
                                state=ChosenDateData.edit_result)
