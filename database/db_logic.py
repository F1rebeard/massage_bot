import logging
import sqlite3 as sql
from datetime import datetime


class Database:
    def __init__(self, db_file):
        self.connection = sql.connect(db_file)
        self.cursor = self.connection.cursor()
        print('Database is online!')

    async def get_user_by_id(self, telegram_id: int):
        """
        Gets users id from database.
        :param telegram_id:
        :return:
        """
    async def get_master_work_graphic(self, telegram_id: int):
        with self.connection:
            work_graphic = self.cursor.execute(
                "SELECT monday, tuesday, wednesday,"
                " thursday, friday, saturday, sunday, days_off"
                " FROM worktime"
                " WHERE master_id = ?", (telegram_id,)
            ).fetchone()[0]
