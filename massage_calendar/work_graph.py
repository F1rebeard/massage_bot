import datetime
import logging

from create_bot import db


async def get_all_working_hours_and_days_off() -> [list, list]:
    """
    Return a list of all days off for a month and list of working hours for
    each master for each weekday.
    :return: master_work_hours = [['0', '0', '0', '0', '0', '0', '0'],
    ['0', [(time(9, 0), time(15, 0))], [(time(2, 0), time(3, 0))]]
    days_off_sum = [2, 6, 15, 31]
    """
    masters_graphics = await db.get_all_masters_work_time()
    # total days off for all masters
    days_off_sum = []
    all_masters_work_time = []
    # getting data for each master
    for master in masters_graphics:
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
        all_masters_work_time.append(weekdays_graphic)
    logging.info(f'all masters worktime: {all_masters_work_time}\n'
                 f'all days off: {days_off_sum}')
    return all_masters_work_time, days_off_sum


def consolidate_intervals(intervals):
    # Sort intervals by start time
    intervals.sort(key=lambda x: x[0])
    consolidated = [intervals[0]]
    for current in intervals[1:]:
        prev = consolidated[-1]
        # If current overlaps prev, merge them
        if current[0] <= prev[1]:
            prev[1] = max(prev[1], current[1])
        # Else just append non-overlapping current interval
        else:
            consolidated.append(current)
    return consolidated


async def consolidated_work_weekday_graphic_for_calendar(
        all_masters_weekday_graphic: list
) -> dict:
    """

    :param all_masters_weekday_graphic:
    :return:
    """
    # Consolidated calendar
    calendar = {
        1: [],  # Monday
        2: [],  # Tuesday
        3: [],  # etc...
    }
    for master in all_masters_weekday_graphic:
        enumerate(master)
        for weekday, hours in enumerate(master):
            logging.info(f'weekday: {weekday}')
            if not calendar[weekday + 1]:
                calendar[weekday + 1] = []
            if not hours or str(hours) == '0':
                calendar[weekday + 1].append(None)
            # If first time seeing this weekday, initialize empty list
            else:
                for start, end in hours:
                    logging.info(f'start: {start}, end: {end}')
                    calendar[weekday + 1].append((start, end))
    # Consolidate intervals
    for weekday in calendar:
        calendar[weekday] = consolidate_intervals(calendar[weekday])
    logging.info(f'Week hours calendar: {calendar}')
    return calendar

