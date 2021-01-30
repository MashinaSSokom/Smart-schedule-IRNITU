from functions.creating_schedule import full_schedule_in_str, full_schedule_in_str_prep
from functions.find_week import find_week
from functions.logger import logger
from tools import keyboards, schedule_processing, statistics

# Глобальная переменная(словарь), которая хранит в себе 3 состояния
# (номер страницы; слово, которые находим; список соответствия для выхода по условию в стейте)
Condition_request = {}


def start_search(bot, message, storage, tz):

    data = message.text
    # ID пользователя
    chat_id = message.chat.id
    # Создаём ключ по значению ID пользователя
    Condition_request[chat_id] = []
    # Зарашиваем данные о пользователе из базы
    user = storage.get_user(chat_id=chat_id)
    # Условие для проверки наличия пользователя в базе
    if 'Основное меню' in data and user:

        # Запуск стейта со значением SEARCH
        msg = bot.send_message(chat_id=chat_id, text="Результаты поиска: ")
        bot.register_next_step_handler(msg, search, bot, storage)

        bot.send_message(chat_id=chat_id, text='Введите название группы или фамилию преподавателя\n'
                         'Например: ИБб-18-1 или Иванов', reply_markup=keyboards.make_keyboard_start_menu())
        statistics.add(action='Основное меню', storage=storage, tz=tz)
    else:

        bot.send_message(chat_id=chat_id, text='Привет\n')
        bot.send_message(chat_id=chat_id, text='Для начала пройдите небольшую регистрацию😉\n')
        bot.send_message(chat_id=chat_id, text='Выберите институт',
                         reply_markup=keyboards.make_keyboard_institutes(storage.get_institutes()))

def search(bot, message, storage):
    """Стейт для работы поиска"""
    # Чат ID пользователя
    chat_id = message.chat.id
    # Данные ввода
    data = message.text
    # Соответствия по группам
    all_found_groups = []
    # Соответствия для преподов
    all_found_prep = []
    # Задаём состояние для первой страницы
    page = 1
    # Логирование для информации в рил-тайм
    logger.info(f'Inline button data: {data}')
    # Условие для первичного входа пользователя
    if (storage.get_search_list(message.text) or storage.get_search_list_prep(message.text)) \
            and Condition_request[chat_id] == []:
        # Результат запроса по группам
        request_group = storage.get_search_list(message.text)
        # Результат запроса по преподам
        request_prep = storage.get_search_list_prep(message.text)
        # Циклы нужны для общего поиска. Здесь мы удаляем старые ключи в обоих реквестах и создаём один общий ключ, как для групп, так и для преподов
        for i in request_group:
            i['search'] = i.pop('name')
        for i in request_prep:
            i['search'] = i.pop('prep_short_name')
        # Записываем слово, которое ищем
        request_word = message.text
        # Склеиваем результаты двух запросов для общего поиска
        request = request_group + request_prep
        # Отправляем в функцию данные для создания клавиатуры
        keyboard = keyboards.make_keyboard_search_group(page, request)
        # Эти циклы записывают группы и преподов в нижнем регистре для удобной работы с ними
        for i in request_group:
            all_found_groups.append(i['search'].lower())
        for i in request_prep:
            all_found_prep.append(i['search'].lower())
        # Создаём общий список
        all_found_results = all_found_groups + all_found_prep
        # Формируем полный багаж для пользователя
        list_search = [page, request_word, all_found_results]
        # Записываем все данные под ключом пользователя
        Condition_request[chat_id] = list_search
        # Выводим результат поиска с клавиатурой (кливиатур формируется по поисковому запросу)

        bot.send_message(chat_id=chat_id, text='Результат поиска', reply_markup=keyboard)

    # Здесь уловия для выхода в основное меню
    elif message.text == "Основное меню":
        del Condition_request[message.from_id]
        bot.send_message(chat_id=chat_id, text='Основное меню', reply_markup=keyboards.make_keyboard_start_menu())
        return

    # Здесь уловие для слова "Дальше"
    elif message.text == "Дальше":
        page = Condition_request[message.from_id][0]
        Condition_request[message.from_id][0] += 1
        request_word = Condition_request[message.from_id][1]
        request_group = storage.get_search_list(request_word)
        request_prep = storage.get_search_list_prep(request_word)
        for i in request_group:
            i['search'] = i.pop('name')
        for i in request_prep:
            i['search'] = i.pop('prep_short_name')
        request = request_group + request_prep
        request = request[26 * page:]
        keyboard = keyboards.make_keyboard_search_group(page + 1, request)
        bot.send_message(chat_id=chat_id, text=f"Страница {page + 1}", reply_markup=keyboard)


    # По аналогии со словом "<==Назад", только обратный процесс
    elif message.text == "<==Назад":
        Condition_request[message.from_id][0] -= 1
        page = Condition_request[message.from_id][0]
        request_word = Condition_request[message.from_id][1]
        request_group = storage.get_search_list(request_word)
        request_prep = storage.get_search_list_prep(request_word)
        for i in request_group:
            i['search'] = i.pop('name')
        for i in request_prep:
            i['search'] = i.pop('prep_short_name')
        request = request_group + request_prep
        request = request[26 * (page - 1):]
        keyboard = keyboards.make_keyboard_search_group(page, request)
        bot.send_message(chat_id=chat_id, text=f"Страница {page}", reply_markup=keyboard)

    # Условие для вывода расписания для группы и преподавателя по неделям
    elif ('На текущую неделю' == data or 'На следующую неделю' == data):
        group = Condition_request[message.from_id][1]
        request_word = Condition_request[message.from_id][1]
        request_group = storage.get_search_list(request_word)
        request_prep = storage.get_search_list_prep(request_word)
        # Если есть запрос для группы, то формируем расписание для группы, а если нет, то для препода
        if request_group:
            schedule = storage.get_schedule(group=group)
        elif request_prep:
            schedule = request_prep[0]
        if schedule['schedule'] == []:
            bot.send_message(chat_id=chat_id, text="Расписание временно недоступно\nПопробуйте позже⏱")
            return

        schedule = schedule['schedule']
        week = find_week()

        # меняем неделю
        if data == 'На следующую неделю':
            week = 'odd' if week == 'even' else 'even'

        week_name = 'четная' if week == 'odd' else 'нечетная'
        if request_group:
            schedule_str = full_schedule_in_str(schedule, week=week)
        elif request_prep:
            schedule_str = full_schedule_in_str_prep(schedule, week=week)

        bot.send_message(chat_id=chat_id, text=f'Расписание {group}\n'f'Неделя: {week_name}', reply_markup=keyboards.make_keyboard_start_menu())
        # Отправка расписания
        schedule_processing.sending_schedule(ans=message, schedule_str=schedule_str)

        return

    # Условия для завершения поиска, тобишь окончательный выбор пользователя
    elif (storage.get_search_list(message.text) or storage.get_search_list_prep(message.text)) and message.text.lower() in \
            (i for i in Condition_request[message.from_id][2]):
        choose = message.text
        Condition_request[message.from_id][1] = choose
        request_word = Condition_request[message.from_id][1]
        request_group = storage.get_search_list(request_word)
        request_prep = storage.get_search_list_prep(request_word)
        for i in request_group:
            i['search'] = i.pop('name')
        for i in request_prep:
            i['search'] = i.pop('prep_short_name')
        if request_group:
            bot.send_message(chat_id=chat_id, text=f"Выберите неделю для группы {choose}",
                             reply_markup=keyboards.make_keyboard_choose_schedule())
        elif request_prep:
            bot.send_message(chat_id=chat_id, text=f"Выберите неделю для преподавателя {request_prep[0]['prep']}",
                             reply_markup=keyboards.make_keyboard_choose_schedule())
        else:
            return
    # Общее исключения для разных случаем, которые могу сломать бота. (Практически копия первого IF)
    else:
        if Condition_request[message.from_id] and storage.get_search_list(message.text) or storage.get_search_list_prep(
                message.text):
            request_group = storage.get_search_list(message.text)
            request_prep = storage.get_search_list_prep(message.text)
            for i in request_group:
                i['search'] = i.pop('name')
            for i in request_prep:
                i['search'] = i.pop('prep_short_name')
            request_word = message.text
            request = request_group + request_prep
            keyboard = keyboards.make_keyboard_search_group(page, request)
            for i in request_group:
                all_found_groups.append(i['search'].lower())
            for i in request_prep:
                all_found_prep.append(i['search'].lower())
            all_found_results = all_found_groups + all_found_prep
            list_search = [page, request_word, all_found_results]
            Condition_request[chat_id] = list_search
            bot.send_message(chat_id=chat_id, text="Результат поиска",
                             reply_markup=keyboard)

        else:
            if len(Condition_request[chat_id]) == 3:
                Condition_request[chat_id][1] = ''
                bot.send_message(chat_id=chat_id, text="Поиск не дал результатов 😕")
                return
            else:
                bot.send_message(chat_id=chat_id, text="Поиск не дал результатов 😕")
                return
