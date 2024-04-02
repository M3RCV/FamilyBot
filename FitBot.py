import telebot
import webbrowser
from telebot import types
import requests
import json

bot = telebot.TeleBot('6638702822:AAHdE4UwysEwsaevsPkA6M9HAg4RtjGI3dg')

weather_API = '96d6a26366cd20bd949ad4fb53196ead'


users = {}

@bot.message_handler(commands = ['start'])
def start(message):
    users[message.chat.id] = {'notifications': 'no'}
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard = True)
    menu_button = types.KeyboardButton("Главное меню")
    keyboard.row(menu_button)
    feedback_button = types.KeyboardButton("Оставить отзыв")
    keyboard.row(feedback_button)
    
    bot.send_message(message.chat.id, f"Привет {message.from_user.first_name}!", reply_markup = keyboard)
    #bot.send_message(message.chat.id, message)

@bot.message_handler(func = lambda message: message.text == "Главное меню")
def menu(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    notifications_button = types.KeyboardButton("Настроить уведомления")
    keyboard.row(notifications_button)
    check_weather = types.KeyboardButton("Погода")
    keyboard.row(check_weather)
    swimming_button = types.KeyboardButton("Тренировка в бассейне")
    training_button = types.KeyboardButton("Тренировка в зале")
    keyboard.row(swimming_button, training_button)
    feedback_button = ("Обратная связь")
    keyboard.row(feedback_button)
    bot.send_message(message.chat.id, "Вы в главном меню!", reply_markup = keyboard)
@bot.message_handler(func = lambda message: message.text == "Обратная связь")
def feed_back(message):
    bot.send_message(message.chat.id, "Напишите ваш отзыв", reply_markup=types.ReplyKeyboardRemove())
    @bot.message_handler()
    def send_msg_admin(message):
        feedback = message.text
        bot.send_message(839663154, feedback, reply_markup=types.ReplyKeyboardRemove())
@bot.message_handler(func = lambda message: message.text == "Погода")
def weather(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    back_to_menu_button = types.KeyboardButton("Вернуться в меню")
    keyboard.row(back_to_menu_button)
    bot.send_message(message.chat.id, "Напишите название город", reply_markup = keyboard)
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
        users[message.chat.id]['notifications'] = 'max'
        print(users)
    elif message.text == "Важные уведомления":
        users[message.chat.id]['notifications'] = 'half'
    else:
        users[message.chat.id]['notifications'] = 'no'

    keyboard = types.InlineKeyboardMarkup()
    back_to_menu_btn = types.InlineKeyboardButton(text = "Да", callback_data="back")
    keyboard.row(back_to_menu_btn)
    del_key = types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, "Готово!", reply_markup=del_key)
    bot.send_message(message.chat.id, "Назад к меню?", reply_markup=keyboard)

@bot.callback_query_handler(func = lambda call: call.data == 'back')
def back_to_menu(call):
    bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.id, text = "Возвращаю в главное меню...")
    menu(call.message)

if __name__ == '__main__':
    bot.infinity_polling()

