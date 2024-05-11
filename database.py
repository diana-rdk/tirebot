import sqlite3 as sq

conn = sq.connect('Services1.db')
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS Services1 (
        service_id INTEGER PRIMARY KEY,
        service_name TEXT,
        service_description TEXT,
        price TEXT
        )""")
conn.commit()


dict1 = "R13-R15: 1500 руб\nR16: 1800 руб\nR17: 2100 руб\nR18: 2400 руб\nR19: 3000 руб\n"
Balance = "R13-R16: 150 руб\nR17: 200 руб\nR18: 250 руб\nR19: 300 руб\n"
Spike = "15 руб/шип"
Resort = "R13-15: 150 руб\nR16: 200 руб\nR17: 250 руб\nR18: 300 руб\nR19: 350 руб\n"
    # Вставьте данные о услугах в таблицу

def is_service_exists(service_name):
    c.execute('SELECT service_id FROM Services1 WHERE service_name = ?', (service_name,))
    return c.fetchone() is not None

def insert_service(service_name, service_description, price):
    if not is_service_exists(service_name):
        c.execute("INSERT INTO Services1 (service_name, service_description, price) VALUES (?, ?, ?)",
                  (service_name, service_description, price))
        conn.commit()


services_data = [
        ("Сезонный шиномонтаж", "В стоимость услуг уже включены:\nдемонтаж/монтаж колёс;\nперебортовка резины и замена шин;\nбалансировка всех четырёх колёс;\nочистка дисков и покрышек\n", dict1),
        ("Балансировка колес", "Балансировка колес для улучшения устойчивости и комфорта вождения.", Balance),
        ("Ошиповка шин", "Нанесение шипов на шины для повышения сцепления с дорогой в зимних условиях.", Spike),
        ("Перебортировка колес", "Перебортировка колес на другие диски для изменения внешнего вида автомобиля.", Resort)
]
for service in services_data:
    insert_service(service[0], service[1], service[2])

conn.commit()


def get_service_by_id(service_id):
    c.execute('SELECT * FROM Services1 WHERE service_id = ?', (service_id,))
    return c.fetchone()

#with sq.connect("book.db") as db:
# cursor = db.cursor()
# #query = """"" CREATE TABLE IF NOT EXISTS book(name TEXT, date DATE, time TIME)"""
# #cursor.execute(query)"""

