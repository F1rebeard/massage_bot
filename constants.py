import os

from dotenv import load_dotenv

load_dotenv()

admin_list = os.getenv("ADMIN_IDS")
ADMIN_IDS = list(map(int, admin_list.split(', ')))

# in minutes
INTERVAL_BTN_MASSAGES: int = 30

RUS_MONTHS = {
    1: 'Январь',
    2: 'Февраль',
    3: 'Март',
    4: 'Апрель',
    5: 'Май',
    6: 'Июнь',
    7: 'Июль',
    8: 'Август',
    9: 'Сентябрь',
    10: 'Октябрь',
    11: 'Ноябрь',
    12: 'Декабрь'
}

WEEKDAYS = {
    'Понедельник': 'monday',
    'Вторник': 'tuesday',
    'Cреда': 'wednesday',
    'Четверг': 'thursday',
    'Пятница': 'friday',
    'Cуббота': 'saturday',
    'Воскресенье': 'sunday'
}

# Виды услуг (продолжительность в минутах, стоимость)
MASSAGES = {
    'general': ('Общий', 90, 2500),
    'back_and_legs': ('Спина и ноги', 60, 2000),
    'hands_and_neck': ('Руки и ШВЗ', 30, 1500),
    'limfo': ('Лимфодренажный', 60, 2000),
    'fire_complex': ('Огненный релакс', 100, 3500),
    'relax': ('Релакс', 90, 2800),
    '4_hands': ('В 4 руки', 60, 5000),
    'pair_massage_short': ('Парный массаж', 60, 5000),
    'pair_massage_long': ('Парный массаж', 90, 6000)
}

OTHER_SERVICE = {
    'manual_therapy': ('Мануальная терапия', 60, 2000),
    'lfk_workout': ('ЛФК занятие', 60, 1000),
}

EXTRA_SERVICE = {
    'pressotherapy_short': ('Прессотерапия', 20, 500),
    'pressotherapy_long': ('Прессотерапия', 40, 800),
    'niddle_therapy': ('Иглотерапия', 30, 800),
    'taping': ('Тейпирование (1 зона)', 15, 600),
    'vacuum': ('Вакуумный массаж банками', 30, 800)
}

# приобрести Подарочные сертификаты на сумму или на количество процедур
