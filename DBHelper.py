import datetime
import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()

now = datetime.datetime.now()
month = [
    'январь', 'февраль', 'март', 'апрель', 'май', 'июнь', 'июль',
    'август', 'сентябрь', 'октябрь', 'ноябрь', 'декабрь'
]

DB_URI = os.getenv('DB')

conn = psycopg2.connect(DB_URI, sslmode="require")
cursor = conn.cursor()


def add_to_db(username: str, chat_id: int, salary=0.0,
              count_sku=0, count_hours=0, count_shifts=0,
              unit_rate_sku=7.3, hourly_rate=124.0):
    """The method adds a new user to the database."""
    cursor.execute(
        'INSERT INTO hard_workers_data (username, chat_id, salary, '
        'count_sku, count_hours, count_shifts, unit_rate_sku, hourly_rate) '
        'VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
        (username, chat_id, salary, count_sku, count_hours,
         count_shifts, unit_rate_sku, hourly_rate)
    )
    conn.commit()


def edit_db(count_sku, count_hours, count_shifts, salary, chat_id):
    """The method edits the data in the database."""
    cursor.execute(
        'UPDATE hard_workers_data SET count_sku = %s, count_hours = %s, '
        'count_shifts = %s, salary = %s WHERE chat_id = %s',
        (count_sku, count_hours, count_shifts, salary, chat_id)
    )
    conn.commit()


def db_salary_information(chat_id):
    """The method displays salary information from the database."""
    cursor.execute(
        'SELECT * from hard_workers_data where chat_id = %s', (chat_id,)
    )
    record = cursor.fetchone()
    return(f'Зарплата за {month[now.month-1]} {now.year} года: '
           f'{record[4]}р.\n'
           f'Количество собраных SKU: {record[2]}\n'
           f'Количество рабочих часов: {record[3]}\n'
           f'Количество смен: {record[6]}')


def rate_sku_db(unit_rate_sku, salary, chat_id):
    """The method changes the information about the rate per SKU in the db."""
    cursor.execute(
        'UPDATE hard_workers_data SET unit_rate_sku = %s, salary = %s '
        'WHERE chat_id = %s', (unit_rate_sku, salary, chat_id)
    )
    conn.commit()


def hourly_rate_db(hourly_rate, salary, chat_id):
    """Changes the information about the rate per working hour in the db."""
    cursor.execute(
        'UPDATE hard_workers_data SET hourly_rate = %s, '
        'salary = %s WHERE chat_id = %s', (hourly_rate, salary, chat_id)
    )
    conn.commit()


def salary_db(chat_id):
    """The method retrieves the user's salary from the database."""
    cursor.execute(
        'SELECT * from hard_workers_data where chat_id = %s', (chat_id,)
    )
    record = cursor.fetchone()
    return record[4]


def sku_db(chat_id):
    """The method gets the number of user SKUs from the database."""
    cursor.execute(
        'SELECT * from hard_workers_data where chat_id = %s', (chat_id,)
    )
    record = cursor.fetchone()
    return record[2]


def hours_db(chat_id):
    """The method gets the user's working hours from the database."""
    cursor.execute(
        'SELECT * from hard_workers_data where chat_id = %s', (chat_id,)
    )
    record = cursor.fetchone()
    return record[3]


def shifts_db(chat_id):
    """The method gets the number of user shifts from the database."""
    cursor.execute(
        'SELECT * from hard_workers_data where chat_id = %s', (chat_id,)
    )
    record = cursor.fetchone()
    return record[6]


def per_sku_db(chat_id):
    """The method gets the user's SKU bid from the database."""
    cursor.execute(
        'SELECT * from hard_workers_data where chat_id = %s', (chat_id,)
    )
    record = cursor.fetchone()
    return record[7]


def per_hours_db(chat_id):
    """The method gets the user's hourly rate from the database."""
    cursor.execute(
        'SELECT * from hard_workers_data where chat_id = %s', (chat_id,)
    )
    record = cursor.fetchone()
    return record[8]


def username_db(chat_id):
    cursor.execute(
        'SELECT username from hard_workers_data where chat_id = %s', (chat_id,)
    )
    return cursor.fetchone()
