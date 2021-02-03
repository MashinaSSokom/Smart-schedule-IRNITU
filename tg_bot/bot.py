import telebot

import pytz

import os
from time import sleep

from tg_bot.actions import commands
from tg_bot.actions.main_menu import schedule, reminders, main_menu
from tg_bot.actions.registration import student_registration, teacher_registration
from tg_bot.functions.storage import MongodbService
from tg_bot.functions.logger import logger
from tg_bot.tools.keyboards import *
from tg_bot.actions.search.prep_and_group_search import start_search, handler_buttons, search
from tg_bot.actions.search.aud_search import start_search_aud, search, handler_buttons_aud

from flask import Flask, request

from tg_bot.tools import statistics

TOKEN = os.environ.get('TOKEN')
HOST_URL = os.environ.get('HOST_URL')

TZ_IRKUTSK = pytz.timezone('Asia/Irkutsk')

bot = telebot.TeleBot(TOKEN, threaded=False)

storage = MongodbService().get_instance()

app = Flask(__name__)

content_schedule = ['Расписание 🗓', 'Ближайшая пара ⏱', 'Расписание на сегодня 🍏', 'На текущую неделю',
                    'На следующую неделю',
                    'Расписание на завтра 🍎', 'Следующая', 'Текущая']

content_main_menu_buttons = ['Основное меню', '<==Назад', 'Список команд', 'Другое ⚡']

content_students_registration = ['institute', 'course', 'group']
content_reminder_settings = ['notification_btn', 'del_notifications', 'add_notifications', 'save_notifications']
content_prep_group = ["found_prep", "prep_list"]
content_aud = ["search_aud", "menu_aud"]


# Обработка запросов от telegram
@app.route(f'/telegram-bot/{TOKEN}', methods=["POST"])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return 'ok', 200


# Проверка работы сервера бота
@app.route('/telegram-bot/status')
def status():
    return 'Бот активен', 200


# ==================== Обработка команд ==================== #

# Команда /start
@bot.message_handler(func=lambda message: message.text in ['Начать', '/start'], content_types=['text'])
def start_handler(message):
    commands.start(bot=bot, message=message, storage=storage, tz=TZ_IRKUTSK)


# Команда /reg
@bot.message_handler(func=lambda message: message.text in ['Регистрация', '/reg'], content_types=['text'])
def registration_handler(message):
    commands.registration(bot=bot, message=message, storage=storage, tz=TZ_IRKUTSK)


# Команда /help
@bot.message_handler(func=lambda message: message.text in ['Помощь', '/help'], content_types=['text'])
def help_handler(message):
    commands.help_info(bot=bot, message=message, storage=storage, tz=TZ_IRKUTSK)


# Команда /map Карта

@bot.message_handler(func=lambda message: message.text in ['Карта', '/map'], content_types=['text'])
def map_handler(message):
    commands.show_map(bot=bot, message=message, storage=storage, tz=TZ_IRKUTSK)


# Команда /about
@bot.message_handler(func=lambda message: message.text in ['О проекте', '/about'], content_types=['text'])
def about_handler(message):
    commands.about(bot=bot, message=message, storage=storage, tz=TZ_IRKUTSK)


# Команда /authors
@bot.message_handler(func=lambda message: message.text in ['Авторы', '/authors'], content_types=['text'])
def authors_handler(message):
    commands.authors(bot=bot, message=message, storage=storage, tz=TZ_IRKUTSK)


# ==================== Обработка Inline кнопок ==================== #
@bot.callback_query_handler(func=lambda message: any(word in message.data for word in content_students_registration))
def student_registration_handler(message):
    """Регистрация студентов"""
    data = message.data
    if data == '{"institute": "Преподаватель"}':
        teacher_registration.start_prep_reg(bot=bot, message=message, storage=storage)
    else:
        student_registration.start_student_reg(bot=bot, message=message, storage=storage)
    logger.info(f'Inline button data: {data}')


@bot.message_handler(func=lambda message: message.text == 'Поиск 🔎', content_types=['text'])
def reminders_info_handler(message):
    """Начало поиска"""
    chat_id = message.chat.id
    bot.send_message(chat_id=chat_id, text='Выберите, что будем искать',
                     reply_markup=make_keyboard_search_goal())


@bot.message_handler(func=lambda message: 'Группы и преподаватели' or 'Аудитории' in message.text,
                     content_types=['text'])
def reminders_info_handler(message):
    """Выбор поиска"""
    data = message.chat.id
    if message.text == "Группы и преподаватели":
        start_search(bot=bot, message=message, storage=storage, tz=TZ_IRKUTSK)
        logger.info(f'Inline button data: {data}')
    else:
        start_search_aud(bot=bot, message=message, storage=storage, tz=TZ_IRKUTSK)
        logger.info(f'Inline button data: {data}')


@bot.callback_query_handler(func=lambda message: 'prep_id' in message.data)
def prep_registration_handler(message):
    teacher_registration.reg_prep_choose_from_list(bot=bot, message=message, storage=storage)


@bot.callback_query_handler(func=lambda message: any(word in message.data for word in content_reminder_settings))
def reminder_settings_handler(message):
    data = message.data
    reminders.reminder_settings(bot=bot, message=message, storage=storage, tz=TZ_IRKUTSK)
    logger.info(f'Inline button data: {data}')


@bot.callback_query_handler(func=lambda message: any(word in message.data for word in content_prep_group))
def prep_registration_handler(message):
    data = message.data
    handler_buttons(bot=bot, message=message, storage=storage, tz=TZ_IRKUTSK)
    logger.info(f'Inline button data: {data}')


@bot.callback_query_handler(func=lambda message: any(word in message.data for word in content_aud))
def prep_registration_handler(message):
    data = message.data
    handler_buttons_aud(bot=bot, message=message, storage=storage, tz=TZ_IRKUTSK)
    logger.info(f'Inline button data: {data}')


@bot.message_handler(func=lambda message: message.text in content_schedule, content_types=['text'])
def schedule_handler(message):
    """Расписание"""
    schedule.get_schedule(bot=bot, message=message, storage=storage, tz=TZ_IRKUTSK)


@bot.message_handler(func=lambda message: message.text == 'Напоминание 📣', content_types=['text'])
def reminders_info_handler(message):
    """Напоминания"""
    reminders.reminder_info(bot=bot, message=message, storage=storage, tz=TZ_IRKUTSK)


@bot.message_handler(func=lambda message: message.text in content_main_menu_buttons, content_types=['text'])
def main_menu_buttons_handler(message):
    """Основные кнопки главного меню"""
    main_menu.processing_main_buttons(bot=bot, message=message, storage=storage, tz=TZ_IRKUTSK)


# ==================== Обработка текста ==================== #
@bot.message_handler(content_types=['text'])
def text(message):
    chat_id = message.chat.id
    data = message.text
    user = storage.get_user(chat_id=chat_id)
    logger.info(f'Message data: {data}')

    if user:
        bot.send_message(chat_id, text='Я вас не понимаю 😞', reply_markup=make_keyboard_start_menu())
    else:
        bot.send_message(chat_id, text='Я вас не понимаю 😞')

    statistics.add(action='bullshit', storage=storage, tz=TZ_IRKUTSK)


if __name__ == '__main__':
    bot.skip_pending = True
    bot.remove_webhook()
    logger.info('Бот запущен локально')
    bot.polling(none_stop=True, interval=0)
else:
    bot.remove_webhook()
    sleep(1)
    bot.set_webhook(url=f'{HOST_URL}/telegram-bot/{TOKEN}')
