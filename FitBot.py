import telebot
from telebot import types
import requests
import json

bot = telebot.TeleBot('6638702822:AAHdE4UwysEwsaevsPkA6M9HAg4RtjGI3dg')

weather_API = '96d6a26366cd20bd949ad4fb53196ead'

all_users = []
users = {"max" : [], "half" : []}

def add_new_id(id, all_users_list):
    if not(id in all_users_list):
        all_users_list.append(id)
        

@bot.message_handler(commands = ['start'])
def start(message):
    add_new_id(message.chat.id, all_users)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard = True)
    menu_button = types.KeyboardButton("Главное меню")
    keyboard.row(menu_button)
    feedback_button = types.KeyboardButton("Оставить отзыв")
    keyboard.row(feedback_button)
    if message.chat.id == 839663154:
        train_button = types.KeyboardButton("Написать тренировку")
        keyboard.row(train_button)
    bot.send_message(message.chat.id, f"Привет {message.from_user.first_name}!", reply_markup = keyboard)

@bot.message_handler(func = lambda message: message.text == "Написать тренировку")
def give_train(message):
    bot.send_message(message.chat.id, "Отправьте id пользователя", reply_markup = types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, get_id)
def get_id(message):
    user_id = int(message.text)
    bot.send_message(message.chat.id, "Напишите тренировку", reply_markup = types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, send_train, user_id)
def send_train(message, user_id: int):
    train = message.text
    bot.send_message(user_id, train)
     
@bot.message_handler(func = lambda message: message.text == "Главное меню")
def menu(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    notifications_button = types.KeyboardButton("Настроить уведомления")
    keyboard.row(notifications_button)
    check_weather = types.KeyboardButton("Погода")
    keyboard.row(check_weather)
    straining_button = types.KeyboardButton("Нужна Тренировка")
    keyboard.row(straining_button)
    feedback_button = ("Оставить отзыв")
    keyboard.row(feedback_button)
    if message.chat.id == 839663154:
        train_button = types.KeyboardButton("Написать тренировку")
        keyboard.row(train_button)
    bot.send_message(message.chat.id, "Вы в главном меню!", reply_markup = keyboard)
    

@bot.message_handler(func = lambda message: message.text == "Нужна Тренировка")
def training(message):
    bot.send_message(message.chat.id, "Опишите тренировку, указав:"+"\n"+"Длительность" \
                     +"\n"+"Цель(Набрать вес, похудеть и т.д)"+"\n"+"Место проведения" \
                     +"\n"+"Ваши пожелания:", reply_markup = types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, train_fb)
def train_fb(message):
    bot.send_message(839663154, message.text)
    bot.send_message(839663154, str(message.chat.id))

@bot.message_handler(func = lambda message: message.text == "Погода")
def weather(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    back_to_menu_button = types.KeyboardButton("Вернуться в меню")
    keyboard.row(back_to_menu_button)
    bot.send_message(message.chat.id, "Напишите название города", reply_markup = keyboard)
    @bot.message_handler()
    def check_weather(message):
        if message.text == "Вернуться в меню":
            menu(message)
        else:
            city = message.text
            weather_now = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_API}&units=metric')
            if not weather_now.ok:
                bot.reply_to(message, "Введите название корректно")
            else:
                data = json.loads(weather_now.text)
                bot.reply_to(message, f'Температура: {data["main"]["temp"]}')
        
@bot.message_handler(func = lambda message: message.text == "Оставить отзыв")
def feed_back(message):
    bot.send_message(message.chat.id, "Напишите ваш отзыв", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, send_msg_to_admin)
def send_msg_to_admin(message):
    feedback = message.text
    bot.send_message(839663154,f"Вам оставил отзыв пользователь {message.from_user.first_name}: " + feedback, reply_markup=types.ReplyKeyboardRemove())
    bot.send_message(message.chat.id, "Спасибо за отзыв!"+"\n"+"Возвращаю в меню...")
    menu(message)

@bot.message_handler(func = lambda message: message.text == "Настроить уведомления")
def notifications(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    max_notifications_button = types.KeyboardButton("Все уведомления")
    keyboard.row(max_notifications_button)
    half_notifications_button = types.KeyboardButton("Важные уведомления")
    no_notifications_button = types.KeyboardButton("Без уведомлений")
    keyboard.row(half_notifications_button, no_notifications_button)

    bot.send_message(message.chat.id, 'Давай определимся с уровнем поддержки!', reply_markup=keyboard)

    bot.register_next_step_handler(message, notification_rang)

def notification_rang(message): # создаем словарь, чтобы далее настроить отправку уведомлений
    if message.text == "Все уведомления":
        if not(message.chat.id in users["max"]):
            users["max"].append(message.chat.id)
            if (message.chat.id in users["half"]):
                users["half"].remove(message.chat.id)
    elif message.text == "Важные уведомления":
        if not(message.chat.id in users["half"]):
            users["half"].append(message.chat.id)
            if (message.chat.id in users["max"]):
                users["max"].remove(message.chat.id)
    else:
        if (message.chat.id in users["max"]):
            users["max"].remove(message.chat.id)
        if (message.chat.id in users["half"]):
            users["half"].remove(message.chat.id)
    print(users)

    bot.send_message(message.chat.id, "Готово!", reply_markup=types.ReplyKeyboardRemove())
    menu(message)

@bot.callback_query_handler(func = lambda call: call.data == 'back')
def back_to_menu(call):
    bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.id, text = "Возвращаю в главное меню...")
    menu(call.message)

if __name__ == '__main__':
    bot.infinity_polling()

