# Smart-schedule-IRNITU
#### Чат боты на базе месенджеров Вконтакте и Telegram для просмотра расписания занятий в Иркутском национальном исследовательском техническом университете;

## Стек технологий:
- Python 3.8
- Docker
- Nginx
- Flask
- Gunicorn

## Проект включает в себя 5 микросервисов:
1. Чат бот для telegram;
2. Чат бот для Вконтакте;
3. Нотификатор - сервис уведомлений на базе месенджеров;
4. Парсер, разработанный специально под расписание сайта ИРНИТУ;
5. Web-manager, для управления базой данных и сервисами.

#### Чат боты
Чат боты были специально написаны на двух самых популярных месенджерах, чтоб ими могла пользоваться любая ворастная аудитория. Простое меню поможет вам пользоваться ботами с еще большим удовольствием! Используя бота на базе VK, аудитория может легко общатся с администраторами по средствам встроенного функциала месенджера, что позволит разработчикам бота быстро реагировать на любую обратную связь пользователей. 
Боты могут:
- Узнать актуальное расписание;
- Нажатием одной кнопки увидеть информацию о ближайшей паре;
- Настроить гибкие уведомления с информацией из расписания, которые будут приходить за определённое время до начала занятия;
- Используя месенджеры вы можете легко получить расписание дома и оно будет у вас под рукой весь день, даже БЕЗ Интернета.

#### Нотификатор
Сервис уведомлений позволяет настроить гибкие уведомления с информацией из расписания, которые будут приходить за определённое время,
указаное вами, до начала занятия. Нотификатор записывает в базу данных значение времени, введенное вами, и выводит уведомление "Пара is coming" в нужный момент.

#### Парсер
Данный сервис разработан индивидуально под сайт ИРНИТУ. Данные парсятся в базу данных, работающую на MongoDB, раз в день или в час, или в минуту...
Все будет так, как решите вы. Всё это позволяет вам содержать в базе данных всегда актуальную иформацию о расписании всего университета!

#### Web-manager
Удобный менеджер, разработанный с использованием HTML, CSS и JavaScript. В нем можно легко контролировать все сервисы в удобном графическом меню с котиками.
Также при каком-то важном сообщении для всех польователей вы можете быстро отправить его одним кликом мыши.
