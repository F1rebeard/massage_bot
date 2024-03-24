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
        with self.connection:
            user = self.cursor.execute(
                'SELECT telegram_id '
                'FROM users '
                'WHERE telegram_id = ?', (telegram_id,)
            ).fetchone()
            logging.info(f'User exists? {user}')
            if user is None:
                return False
            else:
                return True

    async def add_new_user_to_database(self, telegram_id: int):
        """
        Adds new user to database.
        :param telegram_id:
        :return:
        """
        with self.connection:
            self.cursor.execute(
                "INSERT INTO users (telegram_id)"
                " VALUES (?)", (telegram_id,)
            )

    async def update_chosen_date(
            self, telegram_id: int, date: datetime) -> None:
        """
        Update chosen_date column in users table for user
        with chosen telegram_id.
        :param telegram_id:
        :param date:
        :return:
        """
        with self.connection:
            self.cursor.execute(
                "UPDATE users SET chosen_date = ?"
                "WHERE telegram_id = ?", (date, telegram_id)
            )

    async def get_chosen_date(self, telegram_id: int) -> datetime:
        """
        Returns the date from chosen_date column from user table for user with
        selected telegram_id.
        :param telegram_id:
        :return:
        """
        with self.connection:
            chosen_date = self.cursor.execute(
                f" SELECT chosen_date"
                f" FROM users WHERE telegram_id = ?", (telegram_id,)
            ).fetchone()
            return chosen_date[0]

    async def get_master_work_graphic(self, telegram_id: int) -> set:
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

    async def get_all_masters_work_time(self):
        """

        :return:
        """
        with self.connection:
            worktimes = self.cursor.execute(
                "SELECT * FROM worktime"
            ).fetchall()
        return worktimes


