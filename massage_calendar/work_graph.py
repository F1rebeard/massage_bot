import logging
import datetime

from create_bot import db
from constants import INTERVAL_BTN_MASSAGES


async def get_all_working_hours() -> list:
    """
    Return a list of all days off for a month and list of working hours for
    each master for each weekday.
    :return: master_work_hours = [['0', '0', '0', '0', '0', '0', '0'],
    ['0', [(time(9, 0), time(15, 0))], [(time(2, 0), time(3, 0))]]
    days_off_sum = [2, 6, 15, 31]
    """
    masters_graphics = await db.get_all_masters_work_time()
    all_masters_work_time = []
    # getting data for each master
    for master in masters_graphics:
        weekdays_graphic = []
        # weekday from 1 to 7 is Monday, Tuesday, etc.
        # each contains str with working hours
        for weekday in range(1, len(master)-1):
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
        logging.info(f'weekdays_graphic: {weekdays_graphic}')
        all_masters_work_time.append(weekdays_graphic)
        for master in all_masters_work_time:
            logging.info(f'master: {master}')
    return all_masters_work_time


async def get_all_days_off() -> [list[int]]:
    """
    Return a list of all days off for a month for each master.
    :return:
    """
    all_days_off: list = []
    masters_graphics: set = await db.get_all_masters_work_time()
    for master in masters_graphics:
        days_off = master[8]
        if days_off is not None:
            # check if there is one day only
            if len(days_off) == 1:
                days_off = int(days_off)
            else:
                days_off = master[8].split(', ')
        else:
            days_off = []
        logging.info(f'master days off: {days_off}')
        for day in days_off:
            if day not in all_days_off:
                all_days_off.append(int(day))
    return all_days_off


def consolidate_intervals(intervals):
    # Sort intervals by start time
    if not intervals:
        return []
    intervals.sort(key=lambda x: x[0])
    logging.info(f'intervals: {intervals}')
    consolidated = [intervals[0]]
    for current in intervals[1:]:
        prev = consolidated[-1]
        # If current overlaps prev, merge them
        if current[0] <= prev[1]:
            # Create a new merged interval
            merged = [prev[0], max(prev[1], current[1])]
            consolidated[-1] = merged
        else:
            # No overlap, just append
            consolidated.append(current)
    return consolidated


async def work_weekday_graphic_for_calendar(
        all_masters_weekday_graphic: list
) -> dict:
    """

    :param all_masters_weekday_graphic:
    :return:
    """
    # col-1 consolidated, col-2 master-1, col-3 master-2
    calendar = {
        1: [[], [], []],  # Monday
        2: [[], [], []],  # Tuesday
        3: [[], [], []],
        4: [[], [], []],
        5: [[], [], []],
        6: [[], [], []],
        7: [[], [], []]
    }
    count: int = 1
    for master in all_masters_weekday_graphic:
        for weekday, hours in enumerate(master):
            if not hours or hours == '0':
                continue
            # If first time seeing this weekday, initialize empty list
            if not calendar[weekday + 1]:
                calendar[weekday + 1] = []
            for start, end in hours:
                logging.info(f'start: {start}, end: {end}')
                calendar[weekday + 1][0].append((start, end))
            calendar[weekday + 1][1].append(hours)
        count += 1
    # Consolidate intervals
    for weekday in calendar:
        logging.info(f'weekday in calendar: {calendar[weekday][0]}')
        calendar[weekday][0] = consolidate_intervals(calendar[weekday][0])
    return calendar


def generate_time_slots(working_hours: list,
                        massage_duration: int,
                        interval: int) -> list:
    """
    Generates timeslots for massage duration.
    :param working_hours:
    :param massage_duration:
    :param interval:
    :return:
    """
    time_slots = []
    for start, end in working_hours:
        # Create a datetime object for the start time on the current day
        current_datetime = datetime.datetime.combine(
            datetime.datetime.today(), start)
        end_datetime = datetime.datetime.combine(
            datetime.datetime.today(), end)

        while current_datetime + datetime.timedelta(minutes=massage_duration) <= end_datetime:
            time_slots.append(current_datetime.time().strftime("%H:%M"))
            current_datetime += datetime.timedelta(minutes=interval)

    return time_slots


async def get_working_hours_for_date(date: datetime,
                                     weekday_schedule: dict) -> [list,
                                                                 list,

                                                                 list]:
    """
    Retrieves the working hours for a given date.
    :param date: The date for which to retrieve the working hours.
    :param weekday_schedule: The weekday schedule.
    :return: A list of tuples representing the working hours for the given date.
             Each tuple contains the start and end time as datetime.time objects.
    """

    # Get the weekday as an integer (0 = Monday, 6 = Sunday)
    weekday = date.weekday() + 1

    # all_masters_worktime = await get_all_working_hours()
    # Retrieve the master's work schedule from the database or other data source

    # Extract the working hours for the given weekday
    consolidated_hours = weekday_schedule[weekday][0]
    master_1_hours = weekday_schedule[weekday][1]
    master_2_hours = weekday_schedule[weekday][2]

    return consolidated_hours, master_1_hours, master_2_hours


async def get_consolidated_hours_for_date(date: datetime,
                                          weekday_schedule: dict) -> list:
    """

    :param date: The date for which to retrieve the consolidated working hours.
    :param weekday_schedule: The weekday schedule.
    :return:
    """
    weekday = date.weekday() + 1
    consolidated_hours = weekday_schedule[weekday][0]
    return consolidated_hours


async def check_date_is_available(date: datetime,
                                  consolidated_hours: list,
                                  service_time: int) -> tuple[bool, list]:
    """
    Checks if date is available for massage session.
    :param date: date to check for availability.
    :param service_time: length of massage procedure in minutes.
    :return:
    """
    time_slots = generate_time_slots(
            consolidated_hours,
            service_time,
            INTERVAL_BTN_MASSAGES
        )
    if len(time_slots) == 0:
        available = False
    else:
        available = True
    return available, time_slots


async def check_if_date_is_day_off(date: datetime, all_days_of: list) -> bool:
    """
    Checks if the current day of month in calendar is day off or not.
    :param date: The date for which to check if it is day off.
    :param all_days_of: list of all days of the month.
    :return:
    """
    if date.day in all_days_of:
        return True
    else:
        return False

