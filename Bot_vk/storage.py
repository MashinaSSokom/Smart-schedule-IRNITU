import os
from pymongo import MongoClient

MONGO_DB_ADDR = os.environ.get('MONGO_DB_ADDR')
MONGO_DB_PORT = os.environ.get('MONGO_DB_PORT')
MONGO_DB_DATABASE = os.environ.get('MONGO_DB_DATABASE')


class MongodbService(object):
    _instance = None
    _client = None
    _db = None

    @classmethod
    def get_instance(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls.__init__(cls._instance, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self._client = MongoClient(f'mongodb://{MONGO_DB_ADDR}:{MONGO_DB_PORT}')
        self._db = self._client[MONGO_DB_DATABASE]

    def get_data(self, collection) -> list:
        """возвращает список документов из указанной коллекции"""
        return list(self._db[collection].find())

    def save_data(self, collection, data: dict):
        """сохраняет документ в указанную коллекцию"""
        return self._db[collection].insert_one(data)

    def save_institutes(self, institutes: list):
        """сохраняет список институтов в коллекцию institutes"""
        return self._db.institutes.insert_many(institutes)

    def save_courses(self, courses: list):
        """сохраняет список курсов в коллекцию courses"""
        return self._db.courses.insert_many(courses)

    def save_groups(self, groups: list):
        """сохраняет список групп в коллекцию groups"""
        return self._db.groups.insert_many(groups)

    def get_institutes(self) -> list:
        """возвращает список институтов"""
        return list(self._db.institutes.find())

    def get_courses(self, institute='') -> list:
        """возвращает список курсов у определённого института"""
        return list(self._db.courses.find(filter={'institute': {'$regex': f'{institute}*'}}))

    def get_groups(self, institute:str, course: str) -> list:
        """возвращает список групп на определённом курсе в определеннои институте"""
        return list(self._db.groups.find(filter={'institute': {'$regex': f'{institute}*'}, 'course': course}))

    def save_or_update_user(self, chat_id: int, institute='', course='', group='', notifications=0, reminders=[]):
        """сохраняет или изменяет данные пользователя (коллекция users)"""
        update = {'chat_id': chat_id, 'notifications': 0}
        if institute:
            update['institute'] = institute
        if course:
            update['course'] = course
        if group:
            update['group'] = group
        if notifications:
            update['notifications'] = notifications
        if reminders:
            update['reminders'] = reminders

        return self._db.users.update_one(filter={'chat_id': chat_id}, update={'$set': update}, upsert=True)

    def get_user(self, chat_id: int):
        return self._db.users.find_one(filter={'chat_id': chat_id})

    def delete_user_or_userdata(self, chat_id: int, delete_only_course: bool = False):
        """удаление пользователя или курса пользователя из базы данных"""
        if delete_only_course:
            return self._db.users.update_one(filter={'chat_id': chat_id}, update={'$unset': {'course': ''}},
                                             upsert=True)
        return self._db.users.delete_one(filter={'chat_id': chat_id})

    def get_schedule(self, group):
        """возвращает расписание группы"""
        return self._db.schedule.find_one(filter={'group': group})

    # ======================================== VK ======================================== #

    def save_data_vk(self, data: list):
        """сохраняет список id в коллекцию user_id"""
        return self._db.vk_data.insert_many(data)

    def get_user_vk(self, user_id: int):
        """проверяет есть ли id пользователя в db"""
        return self._db.user_id.find_one(filter={'user_id': user_id})

    # def delete_user_or_userdata_vk(self, user_id: int):
    #     """удаление пользователя или курса пользователя из базы данных"""
    #     return self._db.vk_data.delete_one(filter={'user_id': user_id})
    def delete_user_or_userdata_vk(self, user_id: int):
        """удаление пользователя или курса пользователя из базы данных"""
        return self._db.vk_data.remove({'user_id': user_id})