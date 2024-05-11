from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputFile
from aiogram import Bot, Dispatcher, executor, types
from dotenv import load_dotenv
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from database import get_service_by_id, Balance, dict1, Spike, Resort
from insert import get_available_dates, create_keyboard, get_available_time, insert_data_to_db, output_data_from_db, \
    get_id, insert_data_services, plot_statistics, get_appointments_by_date
import os, re
import datetime


load_dotenv()
bot = Bot(os.getenv('TOKEN'))
dp = Dispatcher(bot, storage=MemoryStorage())

kb = InlineKeyboardMarkup(row_width=2)
buttonAbout = InlineKeyboardButton('О нас', callback_data='buttonAbout')
buttonContacts = InlineKeyboardButton('Контакты', callback_data='buttonContacts')
buttonSign = InlineKeyboardButton('Записаться', callback_data='buttonSign')
buttonService = InlineKeyboardButton('Наши услуги', callback_data='buttonService')
buttonBook = InlineKeyboardButton('Мои записи', callback_data='buttonBook')
kb.add(buttonAbout, buttonContacts, buttonSign, buttonService, buttonBook)

kb_admin = InlineKeyboardMarkup(row_width=2)
buttonAbout = InlineKeyboardButton('О нас', callback_data='buttonAbout')
buttonContacts = InlineKeyboardButton('Контакты', callback_data='buttonContacts')
buttonSign = InlineKeyboardButton('Записаться', callback_data='buttonSign')
buttonService = InlineKeyboardButton('Наши услуги', callback_data='buttonService')
buttonBook = InlineKeyboardButton('Мои записи', callback_data='buttonBook')
buttonAdmin = InlineKeyboardButton('Панель администратора', callback_data='buttonAdmin')
kb_admin.add(buttonAbout, buttonContacts, buttonSign, buttonService, buttonBook, buttonAdmin)

admin_panel = InlineKeyboardMarkup(row_width=2)
buttonStatistic = InlineKeyboardButton('Статистика', callback_data='buttonStatistic')
buttonMailing = InlineKeyboardButton('Рассылка', callback_data='buttonMailing')
buttonAdd = InlineKeyboardButton('Добавить запись', callback_data='buttonAdd')
buttonBack = InlineKeyboardButton('<<<Назад', callback_data='buttonBackAd')
buttonAppoint = InlineKeyboardButton('Записи на сегодня', callback_data='buttonAppoint')
admin_panel.add(buttonStatistic, buttonMailing, buttonAdd, buttonBack, buttonAppoint)

kbService = InlineKeyboardMarkup(row_width=1)
buttonTyre = InlineKeyboardButton('Сезонный шиномонтаж', callback_data='buttonTyre')
buttonBalance = InlineKeyboardButton('Балансировка колес', callback_data='buttonBalance')
buttonSpike = InlineKeyboardButton('Ошиповка шин', callback_data='buttonSpike')
buttonResort = InlineKeyboardButton('Перебортировка колес', callback_data='buttonResort')
buttonBack = InlineKeyboardButton('<<<Назад', callback_data='buttonBack')
kbService.add(buttonTyre, buttonBalance, buttonSpike, buttonResort, buttonBack)

kbService2 = InlineKeyboardMarkup(row_width=1)
buttonTyres = InlineKeyboardButton('Сезонный шиномонтаж', callback_data='Сезонный шиномонтаж')
buttonBalances = InlineKeyboardButton('Балансировка колес', callback_data='Балансировка колес')
buttonSpikes = InlineKeyboardButton('Ошиповка шин', callback_data='Ошиповка шин')
buttonResorts = InlineKeyboardButton('Перебортировка колес', callback_data='Перебортировка колес')
buttonBacks = InlineKeyboardButton('<<<Назад', callback_data='buttonBack')
kbService2.add(buttonTyres, buttonBalances, buttonSpikes, buttonResorts, buttonBack)

kbServiceNext = InlineKeyboardMarkup(row_width=1)
buttonBack1 = InlineKeyboardButton('<<<Назад', callback_data='buttonBack1')
kbServiceNext.add(buttonBack1)

kbStat = InlineKeyboardMarkup(row_width=2)
buttonStat = InlineKeyboardButton('Отобразить статистику', callback_data='buttonStat')
buttonBack= InlineKeyboardButton('<<<Назад', callback_data='buttonBack1')
kbStat.add(buttonStat, buttonBack1)

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer(f'{message.from_user.first_name}, здравствуйте! Готов ответить на Ваши вопросы.')
    if message.from_user.id == int(os.getenv('ADMIN_ID')):
        await message.answer('Вы авторизовались как администратор!')
        await message.answer('Что Вас интересует?', reply_markup=kb_admin)
    else:
        await message.answer('Что Вас интересует?', reply_markup=kb)

class BookingStates(StatesGroup):
    CHOOSE_SERVICE = State()
    CHOOSE_DATE = State()
    CHOOSE_TIME = State()
    ENTER_CAR_NUMBER = State()
    ENTER_CAR_MARK = State()
    ENTER_NAME = State()
    ENTER_PHONE_NUMBER = State()
    SIGN = State()


class Mailing(StatesGroup):
    ENTER_TEXT = State()
    ENTER_PHOTO = State()
    CONFIRM = State()

class AddingService(StatesGroup):
    CHOOSE = State()
    ENTER_NAME_SERVICE = State()
    ENTER_DATE = State()
    ENTER_TIME = State()


@dp.message_handler(commands="cancel", state="*")
async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Действие отменено", reply_markup=types.ReplyKeyboardRemove())
    await bot.delete_message(message.from_user.id, message.message_id-1)
    if message.from_user.id == int(os.getenv('ADMIN_ID')):
        await message.answer('Что Вас интересует?', reply_markup=kb_admin)
    else:
        await message.answer('Что Вас интересует?', reply_markup=kb)


@dp.callback_query_handler(lambda c: c.data == 'buttonBook')
async def process_view_booking(callback_query: types.CallbackQuery):
    id = callback_query.from_user.id
    user_id = str(id)
    user_id_from_db = get_id()
    if user_id in user_id_from_db:
        ans = await output_data_from_db(id)
        formated_ans = ""
        for column in ans:
            formated_ans += f"Ваше имя: {column[0]}\n"
            formated_ans += f"Ваш номер телефона: {column[1]}\n"
            formated_ans += f"Услуга: {column[2]}\n"
            formated_ans += f"Дата: {column[3]}\n"
            formated_ans += f"Время: {column[4]}\n"
            formated_ans += f"Номер вашей машины: {column[5]}\n"
            formated_ans += f"Марка вашей машины: {column[6]}\n\n"

        await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
        await bot.send_message(callback_query.from_user.id, f'Ваши записи:\n\n{formated_ans}')
        if callback_query.from_user.id == int(os.getenv('ADMIN_ID')):
            await bot.send_message(callback_query.from_user.id, 'Что Вас интересует?', reply_markup=kb_admin)
        else:
            await bot.send_message(callback_query.from_user.id, 'Что Вас интересует?', reply_markup=kb)
    else:
        await bot.send_message(callback_query.from_user.id, "У вас пока нет записей!")


@dp.callback_query_handler(lambda c: c.data == 'buttonAdmin')
async def process_admin_panel(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    await bot.send_message(callback_query.from_user.id, "Выберите действие: ", reply_markup=admin_panel)


# Обработчик для кнопки администратора
@dp.callback_query_handler(lambda c: c.data == 'buttonStatistic')
async def process_statistics_button(callback_query: types.CallbackQuery):
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    chart_image = plot_statistics()
    await bot.send_photo(callback_query.from_user.id, chart_image, caption='Популярность услуг')
    await bot.send_message(callback_query.from_user.id, "Выберите действие: ", reply_markup=admin_panel)


@dp.callback_query_handler(lambda c: c.data == 'buttonBackAd')
async def process_admin_stat(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    await state.finish()
    await bot.send_message(callback_query.from_user.id, "Что вас интересует?: ", reply_markup=kb_admin)


@dp.callback_query_handler(lambda c: c.data == "buttonMailing")
async def process_mail(callback_query: types.CallbackQuery):
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    await bot.send_message(callback_query.from_user.id, 'Если вы передумали создавать рассылку:/cancel\nВведите текст рассылки')
    await Mailing.ENTER_TEXT.set()


@dp.message_handler(state=Mailing.ENTER_TEXT)
async def enter_text(message: types.Message, state: FSMContext):
    text = message.text
    async with state.proxy() as data:
        data['text'] = text
    await state.update_data(text=text)
    await bot.send_message(message.from_user.id, 'Отправьте фото для рассылки: ')
    await Mailing.ENTER_PHOTO.set()


@dp.message_handler(content_types=['photo'], state=Mailing.ENTER_PHOTO)
async def enter_photo(message: types.Message, state: FSMContext):
    photo = message.photo[0].file_id
    print(photo)
    async with state.proxy() as data:
        data['photo'] = photo
    await state.update_data(photo=photo)
    await bot.send_message(message.from_user.id, 'Подтвердите рассылку (да/нет): ')
    await Mailing.CONFIRM.set()


@dp.message_handler(state=Mailing.CONFIRM)
async def confirm_mailing(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = data['text']
        photo = data['photo']

    if message.text.lower() == 'да':
        user_id_from_db = get_id()
        for user_id in user_id_from_db:
            try:
                await bot.send_photo(chat_id=int(user_id), photo=photo, caption=text)
            except Exception as e:
                print(f"Failed to send to user {user_id}: {e}")

        await bot.send_message(message.from_user.id, 'Рассылка завершена.')
        await state.finish()
        await bot.send_message(message.from_user.id, "Выберите действие: ", reply_markup=admin_panel)
    else:
        await bot.send_message(message.from_user.id, 'Рассылка отменена.')
        await state.finish()
        await bot.send_message(message.from_user.id, "Выберите действие: ", reply_markup=admin_panel)


@dp.callback_query_handler(lambda c: c.data == 'buttonAdd')
async def process_service_add(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    await bot.send_message(callback_query.from_user.id, "Если вы передумали добавлять запись: /cancel\nВведите название услуги: ")
    await AddingService.ENTER_NAME_SERVICE.set()


@dp.message_handler(state=AddingService.ENTER_NAME_SERVICE)
async def process_service_add1(message: types.Message, state: FSMContext):
    service = message.text
    async with state.proxy() as data:
        data['service'] = service
    await state.update_data(service=service)
    await bot.send_message(message.from_user.id, "Введите свободную дату для проведения услуги в формате ДД.ММ.ГГГГ: ")
    await AddingService.ENTER_DATE.set()


@dp.message_handler(state=AddingService.ENTER_DATE)
async def process_adding_date(message: types.Message, state: FSMContext):
    date = message.text.strip()
    if not re.match(r'^\d{2}\.\d{2}\.\d{4}$', date):
        await message.answer('Если вы хотите отменить процесс записи: /cancel\n'
                             "Вы ввели дату в некорректном формате, введите дату в формате ДД.ММ.ГГГГ")
        return

    async with state.proxy() as data:
        data['date'] = date
    await state.update_data(date=date)
    await bot.send_message(message.from_user.id, "Введите время для проведения услуги: ")
    await AddingService.ENTER_TIME.set()



@dp.message_handler(state=AddingService.ENTER_TIME)
async def process_adding_time(message: types.Message, state: FSMContext):
    time = message.text
    if not re.match(r'^\d{2}:\d{2}$', time):
        await message.answer('Если вы хотите отменить процесс записи: /cancel\n'
                             "Вы ввели время в некорректном формате, введите время в формате ЧЧ:ММ")
        return

    async with state.proxy() as data:
        data['time'] = time
    await state.update_data(time=time)
    await insert_data_services(state)
    await state.finish()
    await bot.send_message(message.from_user.id, "Запись создана")
    await bot.send_message(message.from_user.id, "Выберите действие: ", reply_markup=admin_panel)


@dp.callback_query_handler(lambda c: c.data == 'buttonAppoint')
async def process_appoint(callback_query: types.CallbackQuery):
    current_date_str = datetime.datetime.now().strftime("%d.%m.%Y")
    appoint_today = get_appointments_by_date(current_date_str)
    print(appoint_today)
    if not appoint_today:
        await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
        await bot.send_message(callback_query.from_user.id, "На сегодня нет записей!")
        await bot.send_message(callback_query.from_user.id, 'Выберите действие:', reply_markup=admin_panel)
    else:
        text =""
        for appointment in appoint_today:
            text+= f"Имя: {appointment[0]}\n"
            text+= f"Номер телефона: {appointment[1]}\n"
            text+= f"Выбранная услуга: {appointment[2]}\n"
            text+= f"Дата: {appointment[3]}\n"
            text+= f"Время: {appointment[4]}\n\n"

        await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
        await bot.send_message(callback_query.from_user.id, f'Записи на сегодня:\n\n{text}')
        await bot.send_message(callback_query.from_user.id, 'Выберите действие:', reply_markup=admin_panel)

@dp.callback_query_handler(lambda c: c.data == 'buttonSign', state="*")
async def process_sign_callback(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    await BookingStates.CHOOSE_SERVICE.set()
    await bot.send_message(callback_query.from_user.id, 'Выберите услугу:', reply_markup=kbService2)
    print("Work")


@dp.callback_query_handler(
    lambda c: c.data in ['Сезонный шиномонтаж', 'Балансировка колес', 'Ошиповка шин', 'Перебортировка колес',
                         'buttonBack'], state=BookingStates.CHOOSE_SERVICE)
async def process_service_selection(callback_query: types.CallbackQuery, state: FSMContext):
    selected_service = callback_query.data
    available_dates = get_available_dates(selected_service)
    keyboard = create_keyboard(available_dates, with_back_button=False)
    if callback_query.data == 'buttonBack':
        await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
        if callback_query.from_user.id == int(os.getenv('ADMIN_ID')):
            await bot.send_message(callback_query.from_user.id, 'Что Вас интересует?', reply_markup=kb_admin)
            await state.finish()
        else:
            await bot.send_message(callback_query.from_user.id, 'Что Вас интересует?', reply_markup=kb)
            await state.finish()
    else:
        if available_dates:
            await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
            await BookingStates.CHOOSE_DATE.set()
            print("Processing service selection callback")
            async with state.proxy() as data:
                data['selected_service'] = callback_query.data
            selected_service = callback_query.data
            await bot.send_message(callback_query.from_user.id,
                                   'Если вы хотите отменить процесс записи: /cancel\n'
                                   f'Вы выбрали услугу: {selected_service}. Теперь выберите дату:',
                                   reply_markup=keyboard)



@dp.message_handler(state=BookingStates.CHOOSE_DATE)
async def process_date_selection(message: types.Message, state: FSMContext):
    selected_date = message.text
    async with state.proxy() as data:
        service_name = data['selected_service']
    available_time = get_available_time(service_name, selected_date)
    keyboard = create_keyboard(available_time, with_back_button=False)
    if available_time:
        print('date selection')
        async with state.proxy() as data:
            data['selected_date'] = message.text
        selected_date = message.text
        await BookingStates.CHOOSE_TIME.set()
        await message.answer("Спасибо!", reply_markup=types.ReplyKeyboardRemove())
        await bot.send_message(message.from_user.id,
                               f'Вы выбрали дату: {selected_date}. Теперь выберите время:', reply_markup=keyboard)
    else:
        await bot.send_message(message.from_user.id, 'Если вы хотите отменить процесс записи: /cancel\n'
                                                     'Вы ввели некорректную дату, выберите дату из предложеных:')


@dp.message_handler(state=BookingStates.CHOOSE_TIME)
async def process_time_selection(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        service_name = data['selected_service']
        selected_date = data['selected_date']
        data['selected_time'] = message.text
    selected_time = message.text
    choosen_time = get_available_time(service_name, selected_date)
    if selected_time in choosen_time:
        await state.update_data(selected_time=selected_time)
        await message.answer("Спасибо!", reply_markup=types.ReplyKeyboardRemove())
        await bot.send_message(message.from_user.id,
                               f"Вы выбрали время: {selected_time}.\nТеперь укажите гос номер машины в формате А000АВ111:")
        await BookingStates.ENTER_CAR_NUMBER.set()
    else:
        await bot.send_message(message.from_user.id, 'Если вы хотите отменить процесс записи: /cancel\n'
                                                     'Вы ввели некорректное время, выберите время из предложеных:')


@dp.message_handler(state=BookingStates.ENTER_CAR_NUMBER)
async def process_car_number(message: types.Message, state: FSMContext):
    car_number = message.text.lower()
    if not re.match(r'^[авекмнорстух]\d{3}[авекмнорстух]{2}\d{2,3}$', car_number):
        await message.answer('Если вы хотите отменить процесс записи: /cancel\n'
                             "Введите корректный номер машины без пробелов, в формате А000АВ111")
        return
    async with state.proxy() as data:
        data['car_number'] = message.text
    car_number = message.text
    await state.update_data(car_number=car_number)
    await message.answer(f"Вы ввели гос. номер: {car_number}.\nДалее введите марку машины:")
    await BookingStates.ENTER_CAR_MARK.set()

@dp.message_handler(state=BookingStates.ENTER_CAR_MARK)
async def process_car_mark(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['car_mark'] = message.text
    car_mark = message.text
    await state.update_data(car_mark=car_mark)
    await message.answer(f"Вы ввели марку машины: {car_mark}.\nДалее введите Ваше имя:")
    await BookingStates.ENTER_NAME.set()


@dp.message_handler(state=BookingStates.ENTER_NAME)
async def process_name(message: types.Message, state: FSMContext):
    name = message.text
    # Проверка наличия цифр и специальных символов в имени
    if any(char.isdigit() or not char.isalnum() for char in name):
        await message.answer(
            'Если вы хотите отменить процесс записи: /cancel\n'
            "Имя не должно содержать цифры или специальные символы. Пожалуйста, введите корректное имя.")
        return
    async with state.proxy() as data:
        data['name'] = name
    await state.update_data(name=name)
    await message.answer(f"Вы ввели Ваше имя: {name}.\nДалее введите Ваш номер телефона в формате +7...:")
    await BookingStates.ENTER_PHONE_NUMBER.set()

@dp.message_handler(state=BookingStates.ENTER_PHONE_NUMBER)
async def process_phone_number(message: [types.Message, types.CallbackQuery], state: FSMContext):
    phone_number = message.text.strip()
    # Проверка на соответствие российскому формату и отсутствие букв
    if not re.match(r"^(?:\+7|8)[0-9]{10}$", phone_number):
        await message.answer('Если вы хотите отменить процесс записи: /cancel\n'
                             "Введите корректный номер телефона без пробелов и других символов.")
        return
    async with state.proxy() as data:
        data['phone_number'] = phone_number
    await state.update_data(phone_number=phone_number)
    await message.answer(f"Вы ввели Ваш номер телефона: {phone_number}")
    await message.answer(f"Ваша запись:\n\nВаше имя: {data['name']}\nВаш номер телефона: {data['phone_number']}"
                         f"\nУслуга: {data['selected_service']}\nДата: {data['selected_date']}\nВремя: {data['selected_time']}"
                         f"\nНомер вашей машины: {data['car_number']}\nМарка вашей машины: {data['car_mark']}\n\nВы записаны!")
    user_id = message.from_user.id
    await insert_data_to_db(user_id, state)
    await state.finish()
    await message.answer('Что Вас интересует?', reply_markup=kb)


@dp.callback_query_handler()
async def process_callback(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    if callback_query.data == 'buttonAbout':
        with open("about.txt", "r") as file:
            file_content = file.read()  # Считываем содержимое файла
        if callback_query.from_user.id == int(os.getenv('ADMIN_ID')):
            await bot.send_message(callback_query.from_user.id, file_content,
                                   reply_markup=kb_admin)
        else:
            await bot.send_message(callback_query.from_user.id, file_content,
                                   reply_markup=kb)
        print("Work")
    elif callback_query.data == 'buttonContacts':
        with open("contacts.txt", "r") as file:
            file_content = file.read()  # Считываем содержимое файла
        if callback_query.from_user.id == int(os.getenv('ADMIN_ID')):
            await bot.send_message(callback_query.from_user.id, file_content,
                                   reply_markup=kb_admin)
        else:
            await bot.send_message(callback_query.from_user.id, file_content,
                                   reply_markup=kb)

    elif callback_query.data == 'buttonBack':
        if callback_query.from_user.id == int(os.getenv('ADMIN_ID')):
            await bot.send_message(callback_query.from_user.id, 'Что Вас интересует?', reply_markup=kb_admin)
        else:
            await bot.send_message(callback_query.from_user.id, 'Что Вас интересует?', reply_markup=kb)

    elif callback_query.data == 'buttonService':
        await bot.send_message(callback_query.from_user.id, 'Наши услуги:', reply_markup=kbService)

    elif callback_query.data == 'buttonTyre':
        service = get_service_by_id(1)
        imageTyre = InputFile('pics/Сезонный шиномонтаж.jpeg')
        if service:
            service_name, service_description, price = service[1], service[2], service[3]
            message_text = f" Услуга: {service_name}\n{service_description}\nПрайс:\n{dict1}"
        await bot.send_photo(callback_query.from_user.id, imageTyre, caption = message_text, reply_markup=kbServiceNext)

    elif callback_query.data == 'buttonBalance':
        service = get_service_by_id(2)
        imageBalance = InputFile('pics/Балансировка колес.jpeg')
        if service:
            service_name, service_description, price = service[1], service[2], service[3]
            message_text = f" Услуга: {service_name}\n{service_description}\nПрайс за 1 колесо:\n{Balance}"
        await bot.send_photo(callback_query.from_user.id, imageBalance, caption = message_text, reply_markup=kbServiceNext)

    elif callback_query.data == 'buttonSpike':
        service = get_service_by_id(3)
        imageSpike = InputFile('pics/Ошиповка шин.jpeg')
        if service:
            service_name, service_description, price = service[1], service[2], service[3]
            message_text = f" Услуга: {service_name}\n{service_description}\nПрайс: {Spike}"
        await bot.send_photo(callback_query.from_user.id, imageSpike, caption = message_text, reply_markup=kbServiceNext)

    elif callback_query.data == 'buttonResort':
        service = get_service_by_id(4)
        imageResort = InputFile('pics/Перебортировка колес.jpeg')
        if service:
            service_name, service_description, price = service[1], service[2], service[3]
            message_text = f" Услуга: {service_name}\n{service_description}\nПрайс за 1 колесо:\n{Resort}"
        await bot.send_photo(callback_query.from_user.id, imageResort, caption = message_text, reply_markup=kbServiceNext)

    elif callback_query.data == 'buttonBack1':
        await bot.send_message(callback_query.from_user.id, 'Наши услуги:', reply_markup=kbService)


@dp.message_handler()
async def answer(message: types.Message):
    await message.reply('Я не понимаю вас. Для начала работы напишите "/start"')

if __name__ == '__main__':
    executor.start_polling(dp)
