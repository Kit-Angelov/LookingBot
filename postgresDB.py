import psycopg2
import psycopg2.extras
from config import database, admin, password, host


class PostgresDB:

    def __init__(self):
        self.connection = psycopg2.connect(database=database, user=admin, host=host, password=password)
        self.cursor = self.connection.cursor()

    def create_table_users(self):
        with self.connection:
            self.cursor.execute("""CREATE TABLE IF NOT EXISTS users(
                                    user_id INTEGER PRIMARY KEY,
                                    login VARCHAR(64) NOT NULL,
                                    pic_id VARCHAR(100) ,
                                    dob DATE,
                                    sex CHAR(1),
                                    descript TEXT,
                                    black_list TEXT)""")

    def check_user(self, user_id):
        with self.connection:
            self.cursor.execute("SELECT login FROM users WHERE user_id = %s" % user_id)
        return self.cursor.fetchall()

    def get_user_login(self, user_id):
        with self.connection:
            self.cursor.execute("SELECT login FROM users WHERE user_id = %s" % user_id)
        return self.cursor.fetchall()[0][0]

    def get_user(self, user_id):
        with self.connection:
            self.cursor.execute("SELECT * FROM users WHERE user_id = %s" % user_id)
        return self.cursor.fetchall()[0]

    def add_user(self, user_id, login, pic_id, dob, sex, descript):
        with self.connection:
            self.cursor.execute("""INSERT INTO users (
                                    user_id, login, pic_id, dob, sex, descript, black_list)
                                    VALUES (%s, '%s', '%s', '%s', '%s', '%s', '')"""
                                % (user_id, login, pic_id, dob, sex, descript))

    def search_user(self, sex, age):
        age = age.split('-')
        with self.connection:
            self.cursor.execute("""SELECT * FROM users WHERE sex = '%s'
                                    AND EXTRACT(YEAR FROM AGE(dob)) BETWEEN %s AND %s""" % (sex, age[0], age[1]))
        return self.cursor.fetchall()

    def in_black_list(self, black_user_id, user_id):
        with self.connection:
            self.cursor.execute("""UPDATE users SET black_list = black_list + '%s' + ' '
                                    WHERE user_id = %s""" % (black_user_id, user_id))

    def get_black_list(self, user_id):
        with self.connection:
            self.cursor.execute("SELECT black_list FROM users WHERE user_id = %s" % user_id)
        return self.cursor.fetchall()[0][0]

    def delete_from_bl(self, black_user_id, user_id):
        with self.connection:
            self.cursor.execute("""UPDATE users SET black_list = black_list.replace('%s ', '')
                                    WHERE user_id = %s""" % (black_user_id, user_id))

    def close(self):
        self.connection.close()

