import telebot
import json
from time import sleep
import os
from . import DB

from .near_lesson import get_near_lesson

from flask import Flask, request
import requests
import json

from .creating_buttons import makeReplyKeyboard_startMenu, makeInlineKeyboard_chooseInstitute, \
    makeInlineKeyboard_chooseCourses, makeInlineKeyboard_chooseGroups, makeInlineKeyboard_remining, \
    makeInlineKeyboard_custRemining

TOKEN = os.environ.get('TOKEN')
TIMER_URL = os.environ.get('TIMER_URL')

bot = telebot.TeleBot(TOKEN, threaded=False)

app = Flask(__name__)


@app.route(f'/{TOKEN}', methods=["POST"])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return 'ok', 200


# ==================== Обработка команд ==================== #

# Команда /start
@bot.message_handler(commands=['start'])
def start_message(message):
    chat_id = message.chat.id

    # Проверяем есть пользователь в базе данных
    if DB.get_user_info(chat_id):
        DB.del_user_info(chat_id)  # Узадяем пользвателя из базы данных
    print(DB.get_institute())

    bot.send_message(chat_id=chat_id, text='Привет!\n')
    bot.send_message(chat_id=chat_id, text='Для начала пройдите небольшую регистрацию😉\n'
                                           'Выберите институт',
                     reply_markup=makeInlineKeyboard_chooseInstitute(DB.get_institute()))


# Команда /reg
@bot.message_handler(commands=['reg'])
def registration(message):
    chat_id = message.chat.id
    DB.del_user_info(chat_id=chat_id)
    bot.send_message(chat_id=chat_id, text='Пройдите повторную регистрацию😉\n'
                                           'Выберите институт',
                     reply_markup=makeInlineKeyboard_chooseInstitute(DB.get_institute()))


# Команда /help
@bot.message_handler(commands=['help'])
def help(message):
    chat_id = message.chat.id
    bot.send_message(chat_id=chat_id, text='Список команд:\n'
                                           '/reg - повторная регистрация')


# ==================== Обработка Inline кнопок ==================== #
@bot.callback_query_handler(func=lambda call: True)
def handle_query(message):
    chat_id = message.message.chat.id
    message_id = message.message.message_id
    data = message.data
    print(data)

    # После того как пользователь выбрал институт
    if 'inst_id' in data:
        data = json.loads(data)
        courses = DB.get_course(data['inst_id'])

        DB.set_user_inst(chat_id=chat_id, inst_id=data['inst_id'])  # Записываем в базу институт пользователя
        inst = DB.get_user_info(chat_id=chat_id)['inst_name']
        try:
            # Выводим сообщение со списком курсов
            bot.edit_message_text(message_id=message_id, chat_id=chat_id, text=f'{inst}\nВыберите курс',
                                  reply_markup=makeInlineKeyboard_chooseCourses(courses))
        except Exception as e:
            print(f'Error: {e}')
            return

    # После того как пользователь выбрал курс или нажал кнопку назад при выборе курса
    elif 'course_id' in data:
        data = json.loads(data)

        # Если нажали кнопку назад
        if data['course_id'] == 'back':
            DB.del_user_info(chat_id)  # Удаляем информацию об институте пользователя из базы данных
            try:
                bot.edit_message_text(message_id=message_id, chat_id=chat_id,
                                      text='Выберите институт',
                                      reply_markup=makeInlineKeyboard_chooseInstitute(DB.get_institute()))
                return
            except Exception as e:
                print(f'Error: {e}')
                return

        groups = DB.get_group(data['course_id'])

        DB.set_user_course(chat_id=chat_id, course_id=data['course_id'])  # Записываем в базу курс пользователя
        user_info = DB.get_user_info(chat_id=chat_id)
        inst_name = user_info['inst_name']
        kourse = user_info['course']
        try:
            # Выводим сообщение со списком групп
            bot.edit_message_text(message_id=message_id, chat_id=chat_id,
                                  text=f'{inst_name}, {kourse}\nВыберите группу',
                                  reply_markup=makeInlineKeyboard_chooseGroups(groups))
        except Exception as e:
            print(f'Error: {e}')
            return

    # После того как пользователь выбрал группу или нажал кнопку назад при выборе группы
    elif 'group_id' in data:
        data = json.loads(data)

        # Если нажали кнопку назад
        if data['group_id'] == 'back':
            DB.del_user_course(chat_id)  # Удаляем информацию о курсе пользователя из базы данных
            inst_name = DB.get_user_info(chat_id)['inst_name']
            courses = DB.get_course(inst_name=inst_name)

            try:
                # Выводим сообщение со списком курсов
                bot.edit_message_text(message_id=message_id, chat_id=chat_id, text=f'{inst_name}\nВыберите курс',
                                      reply_markup=makeInlineKeyboard_chooseCourses(courses))
                return
            except Exception as e:
                print(f'Error: {e}')
                return

        DB.set_user_group(chat_id=chat_id, group_id=data['group_id'])  # Записываем в базу группу пользователя

        try:
            # Удаляем меню регистрации
            bot.delete_message(message_id=message_id, chat_id=chat_id)
        except Exception as e:
            print(f'Error: {e}')
            return

        bot.send_message(chat_id=chat_id,
                         text='Вы успешно зарегистрировались!😊\n\n'
                              'Для того чтобы пройти регистрацию повторно, воспользуйтесь командой /reg',
                         reply_markup=makeReplyKeyboard_startMenu())

    elif 'remining_btn' in data:
        data = json.loads(data)
        if data['remining_btn'] == 'close':
            try:
                bot.delete_message(message_id=message_id, chat_id=chat_id)
                return
            except Exception as e:
                print(f'Error: {e}')
                return
        time = data['remining_btn']

        try:
            bot.edit_message_text(message_id=message_id, chat_id=chat_id,
                                  text='Настройка напоминаний ⚙\n\n'
                                       'Укажите за сколько минут до начала пары должно приходить сообщение',
                                  reply_markup=makeInlineKeyboard_custRemining(time))
        except Exception as e:
            print(f'Error: {e}')
            return


    elif 'remining_del' in data:
        data = json.loads(data)
        time = data['remining_del']
        if time == 0:
            return
        time -= 5

        try:
            bot.edit_message_reply_markup(message_id=message_id, chat_id=chat_id,
                                          reply_markup=makeInlineKeyboard_custRemining(time))
        except Exception as e:
            print(f'Error: {e}')
            return


    elif 'remining_add' in data:
        data = json.loads(data)
        time = data['remining_add']
        time += 5

        try:
            bot.edit_message_reply_markup(message_id=message_id, chat_id=chat_id,
                                          reply_markup=makeInlineKeyboard_custRemining(time))
        except Exception as e:
            print(f'Error: {e}')
            return

    elif 'remining_save' in data:
        data = json.loads(data)
        time = data['remining_save']

        DB.set_user_reminding(chat_id=chat_id, time=time)

        try:
            bot.edit_message_text(message_id=message_id, chat_id=chat_id, text=get_remining_status(time),
                                  reply_markup=makeInlineKeyboard_remining(time))
        except Exception as e:
            print(f'Error: {e}')
            return


def get_remining_status(time):
    '''Статус напоминаний'''
    if not time or time == 0:
        remining = 'Напоминания выключены ❌\n' \
                   'Воспользуйтесь настройками, чтобы включить'
    else:
        remining = f'Напоминания включены ✅\n' \
                   f'Сообщение придёт за {time} мин до начала пары 😇'
    return remining


# ==================== Обработка текста ==================== #
@bot.message_handler(content_types=['text'])
def text(message):
    chat_id = message.chat.id
    data = message.text

    user_info = DB.get_user_info(chat_id)

    if 'Расписание' in data and user_info:
        try:
            response = requests.get('http://127.0.0.1:5000/get_schedule',
                                    params={'user_info': json.dumps(user_info)})
            # schedule = json.loads(response.text)
            schedule = response.text
        except Exception as e:
            print(f'Error: {e}')
            bot.send_message(chat_id=chat_id, text='Технические неполадки😣 Попробуйте позже')
            return

        group = user_info['group']
        bot.send_message(chat_id=chat_id, text=f'<b>Расписание {group}</b>\n{schedule}', parse_mode='HTML')
    elif 'Ближайшая пара' in data and user_info:
        lessons = [{'date': '3 сентября', 'time': '22:05', 'name': 'Физика', 'aud': 'К-313'},
                   {'date': '3 сентября', 'time': '22:06', 'name': 'Матан', 'aud': 'Ж-310'}]

        near_lesson = get_near_lesson(lessons)

        print(near_lesson)

        if not near_lesson:
            bot.send_message(chat_id=chat_id, text='Сегодня больше пар нет 😎')
            return
        bot.send_message(chat_id=chat_id, text=f'Ближайшая пара {near_lesson["name"]}\n'
                                               f'Аудитория {near_lesson["aud"]}\n'
                                               f'Начало в {near_lesson["time"]}')

    elif 'Напоминания' in data and user_info:
        time = user_info['remining']
        if not time:
            time = 0
        bot.send_message(chat_id=chat_id, text=get_remining_status(time),
                         reply_markup=makeInlineKeyboard_remining(time))
    else:
        bot.send_message(chat_id, text='Я вас не понимаю 😞')
