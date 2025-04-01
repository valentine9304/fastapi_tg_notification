# Сервис задач и уведомлений в Telegram

![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green.svg)
![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)

Это приложение на основе **FastAPI** для управления задачами и отправки уведомлений через Telegram с использованием микросервисной архитектуры. Использует **PostgreSQL** для хранения данных, **Kafka** для обработки сообщений и **Telegram Bot API** для уведомлений.

## Возможности

- Управление задачами (создание, чтение, обновление)
- Уведомления в Telegram с отслеживанием статуса
- Асинхронная обработка с Kafka
- Аутентификация через JWT
- Развертывание через Docker

## Архитектура

- **FastAPI**: Backend
- **aiogram**: Telegram Bot API
- **PostgreSQL**: База Данных
- **Kafka**: Брокер

## Требования

- [Docker](https://www.docker.com/get-started) и [Docker Compose](https://docs.docker.com/compose/install/)
- Python 3.11
- Токен Telegram-бота от [BotFather](https://t.me/BotFather)
- Узнай Ваш Telegram user id обратитесь к боту @userinfobot

## Установка

1. Клонируйте репозиторий:
git clone git@github.com:valentine9304/fastapi_tg_notification.git
2. Создайте .env файл по типу env_example
3. Возьмите API вашего телеграм бота https://t.me/BotFather и добавить его в .env
4. Разверните приложение через docker
docker-compose up --build
5. Swagger развернут по адрессу [http://localhost:8000/docs](http://localhost:8000/docs)
6. Для аутентификации в сервисе , получения JWT токена отправьте "username": admin - по endpoint'e /token
7. Авторизуйтесь в правой вверхнем углу , вставьте Ваш токен

8. Для отправки сообщения через Telegram бота - отправьте сообщение через метод /message по telegram user id

## Автор
:trollface: Валентин :sunglasses:  
