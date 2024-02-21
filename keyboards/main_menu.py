from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


# user buttons
book_session = 'Записаться на массаж 💆‍♂'
active_sessions = 'Активные записи 📅'
ask_the_specialist = 'Консультация у массажиста 🤷🏼'

# admin buttons
my_bookings = 'Мои записи 💆‍♂'
working_time = 'График работы 📅'

user_menu = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1).add(
    book_session, active_sessions, ask_the_specialist
)

admin_menu = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1).add(
    my_bookings, working_time
)
