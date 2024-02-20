import logging
import sqlite3 as sql
from datetime import datetime


class Database:
    def __init__(self, db_file):
        self.connection = sql.connect(db_file)
        self.cursor = self.connection.cursor()
        print('Database is online!')
