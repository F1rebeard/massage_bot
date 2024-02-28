import datetime
import logging

from create_bot import db


async def get_working_hours_for_calendar():
    masters_graphics = await db.get_all_masters_work_time()
    # total days off for all masters
    days_off_sum = []
    # getting data for each master
    for master in masters_graphics:
        master_id = master[0]
        if master[8] is not None:
            days_off = master[8].split(', ')
        else:
            days_off = []
        logging.info(f'days_off: {days_off}')
        for day in days_off:
            if day not in days_off_sum:
                days_off_sum.append(int(day))
        weekdays_graphic = []
        # weekday from 1 to 7 is Monday, Tuesday and etc.
        # each contains str with working hours
        for weekday in range(1, len(master)-1):
            logging.info(f'day number: {weekday}\n'
                         f'day hours: {master[weekday]} type {type(master[weekday])}')
            if str(master[weekday]) == "0" or master[weekday] is None:
                weekdays_graphic.append("0")
            else:
                working_hours = master[weekday].split(", ") if "," in master[weekday] else [master[weekday]]
                day_graphic = []
                for interval in working_hours:
                    start, end = [int(x) for x in interval.split("-")]
                    start_time = datetime.time(start)
                    end_time = datetime.time(end)
                    day_graphic.append((start_time, end_time))
                weekdays_graphic.append(day_graphic)
        logging.info(f'master_id: {master_id}\n'
                     f'weekdays_grapgic: {weekdays_graphic}\n'
                     f'days_off: {days_off}')
