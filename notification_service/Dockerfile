FROM python:3.8

RUN mkdir -p /usr/src/notification_service/
WORKDIR /usr/src/notification_service/


COPY . /usr/src/notification_service/
RUN pip install --no-cache-dir -r requirements.txt

RUN apt update && \
    apt install -y locales && \
    sed -i -e 's/# ru_RU.UTF-8 UTF-8/ru_RU.UTF-8 UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales

ENV LANG ru_RU.UTF-8
ENV LC_ALL ru_RU.UTF-8

CMD ["python3", "start_reminders.py"]