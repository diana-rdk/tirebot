from aiogram import types, executor, bot, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram import Dispatcher as dp_bot
from aiogram.dispatcher.filters.state import State, StatesGroup

from database import get_service_by_id
from main import dp, kbService, kb


class BookingStates(StatesGroup):
    CHOOSE_SERVICE = State()
    CHOOSE_DATE = State()
    CHOOSE_TIME = State()
    ENTER_CAR_INFO = State()

def get_date_keyboard():
    # формирование клавиатуры с датами
    dates = ["Дата 1", "Дата 2", "Дата 3"]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for date in dates:
        button = types.InlineKeyboardButton(text=date, callback_data=f"date:{date}")
        keyboard.add(button)
    return keyboard

def get_time_keyboard():

    # клавиатура с временем
    times = ["Время 1", "Время 2", "Время 3"]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for time in times:
        button = types.InlineKeyboardButton(text=time, callback_data=f"time:{time}")
        keyboard.add(button)
    return keyboard

@dp.callback_query_handler(lambda c: c.data == 'buttonSign')
async def process_sign_callback(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    await BookingStates.CHOOSE_SERVICE.set()
    await bot.send_message(callback_query.from_user.id, 'Выберите услугу:', reply_markup=kbService)


# обработчик для выбора услуги:
@dp.callback_query_handler(lambda c: c.data in ['buttonTyre', 'buttonBalance', 'buttonSpike', 'buttonResort'], state=BookingStates.CHOOSE_SERVICE)
async def process_service_selection(callback_query: types.CallbackQuery, state: FSMContext):
    service_id = {'buttonTyre': 1, 'buttonBalance': 2, 'buttonSpike': 3, 'buttonResort': 4}.get(callback_query.data)
    service = get_service_by_id(service_id)

    if service:
        await state.update_data(service=service)
        await bot.send_message(callback_query.from_user.id, 'Вы выбрали услугу. Теперь выберите дату:', reply_markup=get_date_keyboard)
        await BookingStates.CHOOSE_DATE.set()


@dp.callback_query_handler(lambda c: c.data in ['1.12.2023', '2.12.2023', '3.12.2023', '4.12.2023', '5.12.2023'], state=BookingStates.CHOOSE_DATE)
async def process_date_selection(callback_query: types.CallbackQuery, state: FSMContext):
    selected_date = callback_query.data
    await state.update_data(selected_date=selected_date)
    await bot.send_message(callback_query.from_user.id, f"Вы выбрали дату: {selected_date}.\nТеперь выберите время:", reply_markup=get_time_keyboard())
    await BookingStates.CHOOSE_TIME.set()

@dp.callback_query_handler(lambda c: c.data in ['8:30', '13:00', '14:00', '11:20', '16:00'], state=BookingStates.CHOOSE_TIME)
async def process_time_selection(callback_query: types.CallbackQuery, state: FSMContext):
    selected_time = callback_query.time
    await state.update_data(selected_date=selected_time)
    await bot.send_message(callback_query.from_user.id, f"Вы выбрали время: {selected_time}.\nТеперь укажите гос номер машины:")
    await BookingStates.ENTER_CAR_INFO.set()


@dp.message_handler(state=BookingStates.ENTER_CAR_INFO)
async def process_car_info(message: types.Message, state: FSMContext):
    car_number = message.text
    # Обработка гос. номера машины
    await state.update_data(car_number=car_number)
    await message.reply("Введите гос номер машины:")
    await BookingStates.ENTER_CAR_INFO.set()


# Обработчик для кнопки "Записаться" после выбора всех параметров:
@dp.callback_query_handler(lambda c: c.data == 'buttonSign1', state=BookingStates.ENTER_CAR_INFO)
async def process_sign_confirmation(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    service_name = data['service'][1]
    await bot.send_message(callback_query.from_user.id, f"Вы успешно записаны на {service_name}!\nОжидайте подтверждения.", reply_markup=kb)
    await state.finish()


