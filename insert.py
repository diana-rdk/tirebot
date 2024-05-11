import sqlite3 as sq
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ReplyKeyboardMarkup,  KeyboardButton
import matplotlib.pyplot as plt
import io
import base64

def get_available_dates(service_name):
    conn = sq.connect('book.db')
    cursor = conn.cursor()
    #cursor.execute("SELECT DISTINCT date FROM book WHERE name=?", (service_id))
    #available_dates = [date[0] for date in cursor.fetchall()]
    query = "SELECT DISTINCT date FROM book WHERE name=?"
    cursor.execute(query, (service_name,))
    result = cursor.fetchall()
    all_texts = []
    for item in result:
        text_from_tuple = ""
        for element in item:
            text_from_tuple += element
        all_texts.append(text_from_tuple)
    conn.close()
    return all_texts

def get_available_time(service_name, selected_date):
   conn = sq.connect('book.db')
   cursor = conn.cursor()
   query = "SELECT DISTINCT time FROM book WHERE name=? AND date=?"
   cursor.execute(query, (service_name, selected_date, ))
   result = cursor.fetchall()
   all_texts = []
   for item in result:
       text_from_tuple = ""
       for element in item:
           text_from_tuple += element
       all_texts.append(text_from_tuple)
   conn.close()
   return all_texts

def get_id():
    conn = sq.connect("clients.db")
    cursor = conn.cursor()
    query = ("SELECT DISTINCT id FROM clients")
    cursor.execute(query)
    id = cursor.fetchall()
    all_texts = []
    for item in id:
        text_from_tuple = ""
        for element in item:
            text_from_tuple += element
        all_texts.append(text_from_tuple)
    conn.close()
    return all_texts


def create_keyboard(buttons, with_back_button = False):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for button_text in buttons:
        button = KeyboardButton(text=button_text)
        keyboard.add(button)
    if with_back_button:
        back_button = KeyboardButton(text = '<<<назад')
        keyboard.add(back_button)
    return keyboard

async def insert_data_services(state):
    async with state.proxy() as data:
        service = data['service']
        date = data['date']
        time = data['time']
        conn = sq.connect('book.db')
        cursor = conn.cursor()
        insert_query = """
            INSERT INTO book (name, date, time)
            VALUES (?, ?, ?) """
        cursor.execute(insert_query, (service, date, time))
        conn.commit()

async def insert_data_to_db(user_id,state):
    async with state.proxy() as data:
        id=user_id
        name = data['name']
        phone_number = data['phone_number']
        selected_service = data['selected_service']
        selected_date = data['selected_date']
        selected_time = data['selected_time']
        car_number = data['car_number']
        car_mark = data['car_mark']

    try:
        conn = sq.connect('clients.db')
        cursor = conn.cursor()
        insert_query = """
            INSERT INTO clients (id, name, phone_number, selected_service, selected_date, selected_time, car_number, car_mark)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?) """
        cursor.execute(insert_query,
                       (id, name, phone_number, selected_service, selected_date, selected_time, car_number, car_mark))
        conn.commit()

        conect = sq.connect('book.db')
        cur = conect.cursor()
        delete_query = """ DELETE FROM book WHERE name=? AND date=? AND time=?"""
        cur.execute(delete_query, (selected_service, selected_date, selected_time))
        conect.commit()

    except sq.Error as e:
        print(f"Ошибка при вставке данных в базу данных: {e}")

    finally:
        if conn:
            conn.close()

async def output_data_from_db(us_id):
    conn = sq.connect('clients.db')
    cursor = conn.cursor()
    query = ("SELECT DISTINCT name, phone_number, selected_service, selected_date, selected_time, car_number, car_mark FROM clients WHERE id=?")
    cursor.execute(query, (us_id,))
    final = cursor.fetchall()
    print(final)
    return final
    cursor.close()

def plot_statistics():
    conn = sq.connect('clients.db')
    cursor = conn.cursor()
    query = "SELECT selected_service, COUNT(*) FROM clients GROUP BY selected_service"
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()

    if results:
        # Разделение результатов на два списка: названия услуг и соответствующие количества записей
        services, counts = zip(*results)

        #Построение графика
        figsize = (10, 15)
        fig, ax = plt.subplots(figsize = figsize)
        ax.bar(services, counts, color='royalblue')

        plt.xlabel('Название услуги', fontsize=20, fontweight='bold', color='steelblue')
        plt.ylabel('Количество записей', fontsize=20, fontweight='bold', color='steelblue')
        plt.title('Популярность услуг', fontsize=25, fontweight='bold', color='steelblue')

        # Сохранение графика в байтовом объекте
        image_stream = io.BytesIO()
        plt.savefig(image_stream, format='png')
        image_stream.seek(0)
        plt.close()

        return image_stream
    else:
        print("Нет данных для построения графика.")
        return None

import datetime


def get_appointments_by_date(date_str):
    conn = sq.connect("clients.db")
    cursor = conn.cursor()
    query = """SELECT name, phone_number, selected_service, selected_date, selected_time FROM clients WHERE selected_date = ?"""
    cursor.execute(query, (date_str,))
    appointments = cursor.fetchall()

    conn.close()

    return appointments






