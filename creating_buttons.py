from telebot import types
import json


# Создаём основные кнопки
def makeReplyKeyboard_startMenu():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=True)
    btn1 = types.KeyboardButton('Расписание')
    btn2 = types.KeyboardButton('Ближайшая пара')
    btn3 = types.KeyboardButton('Настройка уведомлений')
    markup.add(btn1, btn2)
    markup.add(btn3)
    return markup


# Кнопки выбора института
def makeInlineKeyboard_chooseInstitute(institute_list=[]):
    markup = types.InlineKeyboardMarkup()
    for inst in institute_list:
        name = inst['name']
        institute_id = inst['inst_id']
        data = json.dumps({"inst_id": institute_id})
        markup.add(types.InlineKeyboardButton(text=name, callback_data=data))
    return markup


# Кнопки выбора курса
def makeInlineKeyboard_chooseCourses(courses_list=[]):
    markup = types.InlineKeyboardMarkup()
    for course in courses_list:
        name = course['name']
        course_id = course['course_id']
        data = json.dumps({"course_id": course_id})
        markup.add(types.InlineKeyboardButton(text=name, callback_data=data))

    # Кнопка назад
    data = json.dumps({"course_id": "back"})
    markup.add(types.InlineKeyboardButton(text='<', callback_data=data))
    return markup


# Кнопки выбора группы
def makeInlineKeyboard_chooseGroups(groups_list=[]):
    markup = types.InlineKeyboardMarkup()
    for group in groups_list:
        name = group['name']
        courses_id = group['group_id']
        data = json.dumps({"group_id": courses_id})
        markup.add(types.InlineKeyboardButton(text=name, callback_data=data))
    # Кнопка назад
    data = json.dumps({"group_id": "back"})
    markup.add(types.InlineKeyboardButton(text='<', callback_data=data))
    return markup
