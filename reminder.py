def remining_info(time):
    if not time or time == 0:
        remining = 'Напоминания выключены ❌\n' \
                   'Воспользуйтесь настройками, чтобы включить'
    else:
        remining = f'Напоминания включены ✅\n' \
                        f'Сообщение придёт за {time} мин до начала пары 😇'
    return remining