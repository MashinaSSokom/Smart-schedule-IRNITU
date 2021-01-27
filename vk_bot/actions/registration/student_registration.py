from vkbottle.bot import Message

from actions import commands
from tools import keyboards, statistics

from functions.notifications import calculating_reminder_times, get_notifications_status


def name_institutes(institutes=[]):
    """ Храним список всех институтов """

    list_institutes = []
    for i in institutes:
        name = i['name']
        list_institutes.append(name)
    return list_institutes


def name_courses(courses=[]):
    """ Храним список всех курсов """

    list_courses = []
    for i in courses:
        name = i['name']
        list_courses.append(name)
    return list_courses


def name_groups(groups=[]):
    """ Храним список всех групп """

    list_groups = []
    for i in groups:
        name = i['name']
        list_groups.append(name)
    return list_groups


async def start_student_reg(ans: Message, storage, tz):
    chat_id = ans.from_id
    message_inst = ans.text
    message = ans.text
    user = storage.get_vk_user(chat_id)

    # Сохраняет в месседж полное название универ для корректного сравнения
    institutes = name_institutes(storage.get_institutes())
    for institute in institutes:
        if len(message_inst) > 5:
            if message_inst[:-5] in institute:
                message_inst = institute

    # Если пользователя нет в базе данных
    if not user:
        institutes = name_institutes(storage.get_institutes())
        # Смотрим выбрал ли пользователь институт
        if message_inst in institutes:
            # Если да, то записываем в бд
            storage.save_or_update_vk_user(chat_id=chat_id, institute=message_inst)
            await ans.answer(f'Вы выбрали: {message_inst}\n')
            await ans.answer('Выберите курс.',
                             keyboard=keyboards.make_keyboard_choose_course_vk(storage.get_courses(message_inst)))
        else:
            await commands.start(ans=ans, chat_id=chat_id, storage=storage)

    # Если нажал кнопку Назад к институтам
    elif message == "Назад к институтам" and not 'course' in user.keys():
        await ans.answer('Выберите институт.', keyboard=keyboards.make_keyboard_institutes(storage.get_institutes()))
        storage.delete_vk_user_or_userdata(chat_id=chat_id)
        return

    # Если нажал кнопку Назад к курсам
    elif message == "Назад к курсам" and not 'group' in user.keys():

        await ans.answer('Выберите курс.', keyboard=keyboards.make_keyboard_choose_course_vk(
            storage.get_courses(storage.get_vk_user(chat_id=chat_id)['institute'])))
        storage.delete_vk_user_or_userdata(chat_id=chat_id, delete_only_course=True)
        return

    # Регистрация после выбора института
    elif not 'course' in user.keys():
        institute = user['institute']
        course = storage.get_courses(institute)
        # Если нажал кнопку курса
        if message in name_courses(course):
            # Записываем в базу данных выбранный курс
            storage.save_or_update_vk_user(chat_id=chat_id, course=message)
            groups = storage.get_groups(institute=institute, course=message)
            groups = name_groups(groups)
            await ans.answer(f'Вы выбрали: {message}\n')
            await ans.answer('Выберите группу.', keyboard=keyboards.make_keyboard_choose_group_vk(groups))
            return
        else:
            await ans.answer('Не огорчай нас, мы же не просто так старались над клавиатурой 😼👇🏻')
        return

    # Регистрация после выбора курса
    elif not 'group' in user.keys():
        institute = user['institute']
        course = user['course']
        groups = storage.get_groups(institute=institute, course=course)
        groups = name_groups(groups)
        # Если нажал кнопку группы
        if message in groups:
            # Записываем в базу данных выбранную группу
            storage.save_or_update_vk_user(chat_id=chat_id, group=message)
            await ans.answer('Вы успешно зарегистрировались!😊\n\n'
                             'Для того чтобы пройти регистрацию повторно, напишите сообщение "Регистрация"\n'
                             , keyboard=keyboards.make_keyboard_start_menu())
        else:
            if message == "Далее":
                await ans.answer('Выберите группу.', keyboard=keyboards.make_keyboard_choose_group_vk_page_2(groups))
            elif message == "Назад":
                await ans.answer('Выберите группу.', keyboard=keyboards.make_keyboard_choose_group_vk(groups))
            else:
                await ans.answer('Я очень сомневаюсь, что твоей группы нет в списке ниже 😉')
        return

    elif 'Напоминание 📣' in message and user.get('group'):
        time = user['notifications']
        # Проверяем стату напоминания
        if not time:
            time = 0
        await ans.answer(f'{get_notifications_status(time)}', keyboard=keyboards.make_inline_keyboard_notifications())

        statistics.add(action='Напоминание', storage=storage, tz=tz)

    elif 'Настройки' in message and user.get('group'):
        time = user['notifications']
        await ans.answer('Настройка напоминаний ⚙\n\n'
                         'Укажите за сколько минут до начала пары должно приходить сообщение',
                         keyboard=keyboards.make_inline_keyboard_set_notifications(time))
        statistics.add(action='Настройки', storage=storage, tz=tz)

    elif '-' == message:
        time = user['notifications']
        if time == 0:
            await ans.answer('Хочешь уйти в минус?', keyboard=keyboards.make_inline_keyboard_set_notifications(time))
            return
        time -= 5
        # Отнимаем и проверяем на положительность
        if time <= 0:
            time = 0
        storage.save_or_update_vk_user(chat_id=chat_id, notifications=time)
        await ans.answer('Минус 5 минут', keyboard=keyboards.make_inline_keyboard_set_notifications(time))
        return

    elif '+' == message:
        time = user['notifications']
        time += 5
        storage.save_or_update_vk_user(chat_id=chat_id, notifications=time)
        await ans.answer('Плюс 5 минут', keyboard=keyboards.make_inline_keyboard_set_notifications(time))

    elif 'Сохранить' in message:

        # Сохраняем статус в базу
        time = user['notifications']

        group = storage.get_vk_user(chat_id=chat_id)['group']

        if storage.get_vk_user(chat_id=chat_id)['course'] == "None":
            schedule = storage.get_schedule_prep(group=group)['schedule']
        else:
            schedule = storage.get_schedule(group=group)['schedule']
        if time > 0:
            reminders = calculating_reminder_times(schedule=schedule, time=int(time))
        else:
            reminders = []
        storage.save_or_update_vk_user(chat_id=chat_id, notifications=time, reminders=reminders)

        await ans.answer(f'{get_notifications_status(time)}', keyboard=keyboards.make_keyboard_start_menu())


    elif 'Основное меню' in message and user.get('group'):
        await ans.answer('Основное меню', keyboard=keyboards.make_keyboard_start_menu())
        statistics.add(action='Основное меню', storage=storage, tz=tz)

    elif '<==Назад' == message and user.get('group'):
        await ans.answer('Основное меню', keyboard=keyboards.make_keyboard_start_menu())

    elif 'Далее' in message:
        await ans.answer('Далее', keyboard=keyboards.make_keyboard_choose_group_vk_page_2())


    elif 'Список команд' == message and user.get('group'):
        await ans.answer('Список команд:\n'
                         'Авторы - список авторов \n'
                         'Регистрация- повторная регистрация\n'
                         'Карта - карта университета', keyboard=keyboards.make_keyboard_commands())

        statistics.add(action='help', storage=storage, tz=tz)
        return

    elif 'Другое ⚡' == message and user.get('group'):
        await ans.answer('Другое', keyboard=keyboards.make_keyboard_extra())
        statistics.add(action='Другое', storage=storage, tz=tz)
        return

    elif 'Поиск 🔎' == message and user.get('group'):

        await ans.answer('Выберите, что будем искать', keyboard=keyboards.make_keyboard_search())



    else:
        await ans.answer('Такому ещё не научили 😇, знаю только эти команды:\n'
                         'Авторы - список авторов \n'
                         'Регистрация - повторная регистрация\n'
                         'Карта - карта университета')
        statistics.add(action='bullshit', storage=storage, tz=tz)
