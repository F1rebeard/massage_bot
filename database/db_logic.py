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
        """
        Gets working graphic from database.
        :param telegram_id:
        :return:
        """
        with self.connection:
            work_graphic = self.cursor.execute(
                "SELECT monday, tuesday, wednesday,"
                " thursday, friday, saturday, sunday, days_off"
                " FROM worktime"
                " WHERE master_id = ?", (telegram_id,)
            ).fetchone()
        logging.info(work_graphic)
        return work_graphic

    async def update_master_worktime(
            self,
            telegram_id: int,
            work_graphic: str,
            query_data: str
    ):
        """

        :param telegram_id:
        :param work_graphic:
        :param query_data:
        :return:
        """
        column_name = query_data
        with self.connection:
            self.cursor.execute(
                f"UPDATE worktime "
                f"SET {column_name} = ? "
                f"WHERE master_id = ?", (work_graphic, telegram_id)
            )
        logging.info(f'День недели: {column_name}'
                     f' c новым временем {work_graphic}')
