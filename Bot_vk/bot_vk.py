from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType
from functions.storage import MongodbService
from vk_api.utils import get_random_id
from vk_api import VkUpload
from Bot_vk.functions import creating_buttons_vk
import vk_api
import time
import json
import vk
import os


token = os.environ.get('TOKEN_VK')

authorize = vk_api.VkApi(token=token)

longpoll= VkLongPoll(authorize)

storage = MongodbService().get_instance()

MAX_CALLBACK_RANGE = 41

def parametres_for_buttons_start_menu_vk(text, color):
    '''Возвращает параметры кнопок'''
    return {
        "action": {
        "type": "text",
        "payload": "{\"button\": \"" + "1" + "\"}",
        "label": f"{text}"
        },
        "color": f"{color}"
        }

def make_inline_keyboard_choose_institute_vk(institutes=[]):
    """Кнопки выбора института"""
    keyboard = {
        "one_time": False
    }
    list_keyboard_main = []
    for institute in institutes:
        if len(institute['name']) >= MAX_CALLBACK_RANGE:
            name = sep_space(institute['name'])
        else:
            name = institute['name']
        list_keyboard = []
        list_keyboard.append(parametres_for_buttons_start_menu_vk(f'{name}', 'primary'))
        list_keyboard_main.append(list_keyboard)
    keyboard['buttons'] = list_keyboard_main
    return keyboard

def sep_space(name):
    '''Обрезает длину института, если тот больше 40 символов'''
    dlina = abs(len(name) - MAX_CALLBACK_RANGE)
    name = name[:len(name) - dlina-1]
    return name

def sender_zero(id, text):
    '''Отправки сообщения + пустое меню'''
    keyboard = json.dumps(keyboard_zero, ensure_ascii=False).encode('utf-8')
    keyboard = str(keyboard.decode('utf-8'))
    authorize.method('messages.send', {'user_id': id, 'message': text, 'random_id': 0, 'keyboard': keyboard})

def sender_institutes(id, text):
    '''Отправки сообщения + меню с институтами для регистрации'''
    keyboard = json.dumps(keyboard_institutes, ensure_ascii=False).encode('utf-8')
    keyboard = str(keyboard.decode('utf-8'))
    authorize.method('messages.send', {'user_id': id, 'message': text, 'random_id': 0, 'keyboard': keyboard})

def sender_menu(id, text):
    '''Отправки сообщения + главное меню'''
    keyboard = json.dumps(keyboard_menu, ensure_ascii=False).encode('utf-8')
    keyboard = str(keyboard.decode('utf-8'))
    authorize.method('messages.send', {'user_id': id, 'message': text, 'random_id': 0, 'keyboard': keyboard})

# Клавиатуры для разных этапов
keyboard_menu = {
    "one_time": False,
    "buttons": [
        [parametres_for_buttons_start_menu_vk('Расписание', 'primary'),
         parametres_for_buttons_start_menu_vk('Ближайшая пара', 'primary')],
        [parametres_for_buttons_start_menu_vk('Напоминание', 'default')]
    ]}

keyboard_zero = {
    "one_time": False,
    "buttons": []
}

keyboard_institutes = make_inline_keyboard_choose_institute_vk(storage.get_institutes())


def start(user_id, message):
    '''Проверяем есть пользователь в базе данных'''
    if storage.get_user_vk(user_id):
        storage.delete_user_or_userdata_vk(user_id) # удаляем пользователя
    # Запись в базу id
    user_id_list = []
    user_id_dict = {}
    user_id_dict['user_id'] = id
    user_id_list.append(user_id_dict)

    sender_zero(user_id, 'Привет!\n')
    sender_zero(user_id, 'Для начала пройдите небольшую регистрацию😉\n')

    #Открывает кнопки для выбора институ при регистрации
    sender_institutes(user_id, 'Выберите институт!\n')

def reg(user_id, message):
    '''Почти копия функции start'''
    sender_zero(user_id, 'Вы уже были ранее зарегистрированы!\n')
    sender_zero(user_id, 'Если хотите пройти повторну регистрацию, воспользуйтесь командой /reg\n')
    pass

def help(user_id, message):
    sender_zero(user_id, 'Вы можете использовать команду /reg для повторной регистрации!\n')
    sender_zero(user_id, 'Вы можете использовать команду /help для получения списка доступных команд!\n')
    main()

def main():
    '''Ожидает сообщения от пользователя и даёт ответную реакцию'''
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                id = event.user_id
                message = event.text.lower()
                if message == '/reg':
                    reg(id, message)
                elif message == '/help':
                    help()
                else:
                    start(id, message)


if __name__ == "__main__":
    main()

