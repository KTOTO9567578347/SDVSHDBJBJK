import sqlite3 as sql
import datetime
import threading
import dateutil.parser as date_parser

import datetime as dt
import time as t

import dateutil.parser

def check_time(last_send_time, interval_time):
    res = dt.datetime.now() - dt.timedelta(seconds=int(interval_time)) >= date_parser.parse(last_send_time)
    return res

class DB:
    def __init__(self) -> None:
        connection = sql.connect('./database/weatherbot.db')
        cursor = connection.cursor()

        cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS users (
        telegram_id varchar(255) PRIMARY KEY,
        chat_id varchar(255),
        city varchar(255),
        last_sent_time INTEGER,
        sent_interval INTEGER
        );
        '''
        )
        connection.commit()
        connection.close()

        self.insertion_que = "INSERT INTO users VALUES (?, ?, ?, ?, ?)"
        self.city_change_que = "UPDATE users SET city = ? WHERE telegram_id = ?;"
        self.interval_change_que = "UPDATE users SET sent_interval = ? WHERE telegram_id = ?;"
        self.time_refresh_que = "UPDATE users SET last_sent_time = ? WHERE telegram_id = ?;"
        self.is_exists_que = "SELECT Count(telegram_id) FROM users WHERE telegram_id = ?;"
        self.user_city_que = "SELECT city FROM users WHERE telegram_id = ?"
        self.user_time_que = "SELECT last_sent_time FROM users WHERE telegram_id = ?"
        self.user_delete_que = "DELETE FROM users WHERE telegram_id = ?"

    def create_new_user(self, username, chat_id):
        try:
            connection = sql.connect('./database/weatherbot.db')
            cursor = connection.cursor()
            cursor.execute(self.insertion_que, (username, chat_id, "Москва", datetime.datetime.now(), 43200))
            connection.commit()
            connection.close()
            return True
        except:
            return False
    
    def delete_user(self, username):
        connection = sql.connect('./database/weatherbot.db')
        cursor = connection.cursor()
        cursor.execute(self.user_delete_que, (username,))
        connection.commit()
        connection.close()
    
    def change_user_city(self, username, city):
        connection = sql.connect('./database/weatherbot.db')
        cursor = connection.cursor()
        cursor.execute(self.city_change_que, (city, username))
        connection.commit()
        connection.close()

    def change_user_interval(self, username, interval):
        connection = sql.connect('./database/weatherbot.db')
        cursor = connection.cursor()
        cursor.execute(self.interval_change_que, (interval, username))
        connection.commit()
        connection.close()

    def refresh_user_time(self, username):
        connection = sql.connect('./database/weatherbot.db')
        cursor = connection.cursor()
        cursor.execute(self.time_refresh_que, (dt.datetime.now(), username))
        connection.commit()
        connection.close()

    def check_is_user_exists(self, username):
        connection = sql.connect('./database/weatherbot.db')
        cursor = connection.cursor()
        res = cursor.execute(self.is_exists_que, (username,)).fetchone()
        connection.commit()
        connection.close()
        return bool(res[0])
    
    def get_user_city(self, username):
        connection = sql.connect('./database/weatherbot.db')
        cursor = connection.cursor()
        res = cursor.execute(self.user_city_que, (username,)).fetchone()
        connection.commit()
        connection.close()
        return str(res[0])
    
    def get_user_last_time(self, username):
        connection = sql.connect('./database/weatherbot.db')
        cursor = connection.cursor()
        res = cursor.execute(self.user_time_que, (username,)).fetchone()
        connection.commit()
        connection.close()
        return date_parser.parse(res[0])
    
    def get_overtimed_users(self):
        connection = sql.connect('./database/weatherbot.db')
        connection.create_function("return_overtimed", 2, check_time)
        overtimed_query = "SELECT telegram_id, chat_id, city FROM users WHERE return_overtimed(last_sent_time, sent_interval)"
        cursor = connection.cursor()
        res = cursor.execute(overtimed_query).fetchall()
        connection.commit()
        connection.close()
        return res
