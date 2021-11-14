Проект команды FLASK LOVERS

Персональный ассистент "BOT"

Возможности: 

        1. Управление книгой контактов (создание, редактирование, поиск, удаление контактов)
        2. Управление записной книжкой (создание, редактирование, поиск, добавление тегов, удаление заметок)
        3. Управление файловым репозиторием (загрузка, сортировка, скачивание, удаление файлов)
        4. Новостная лента по избранным ресурсам

Интерфейс:

Аналог популярного для телеграмм-ботов интрефейса - основные функции запускаются текстовыми командами, 
которые пользователь отдает на английском языке. Логика взаимодействия внутри функций реализована на веб-формах.

Приложение предоставляет каждому пользователю приватную, защищенную от других пользователей область данных.


Инструкция по установке и запуску приложения:

**1. Heroku
**
Приложение уже запущено и доступно для работы по адресу:

https://bot-web-project2.herokuapp.com/



**2. Docker
**
Образ приложения доступен на DockerHub.

Для установки и запуска необходимо выполнить следующую последовательность действий:

- Установить приложение docker, отсюда: https://docs.docker.com/get-docker/

- загрузить docker-образ командой: docker pull mathteacher/bot_project2_web
	

- Создать файл docker-compose.yml в директории, из которой вы разворачиваете приложение:


        version: '3.9'
        services:
          web:
            image: mathteacher/bot_project2_web
            container_name: bot-flask
            environment:
              - FLASK_APP=main.py:init_app()
              - DB_USERNAME=change_for_your_user_name
              - DB_PASSWORD=change_for_your_user_password
              - DB_HOST=pg-project2
              - SECRET_KEY=change_for_your_secret_key
            ports:
              - '5000:5000'
            depends_on:
              - db
            networks:
              - app-network

          db:
            image: postgres
            container_name: pg-project2
            restart: unless-stopped
            environment:
              POSTGRES_USER: change_for_your_user_name
              POSTGRES_PASSWORD: change_for_your_user_password
              POSTGRES_DB: contact_book
            volumes:
              - .\pg_data:/var/lib/postgresql/data
            networks:
              - app-network
            ports:
              - '5432:5432'

        networks:
          app-network:
            driver: bridge


  важно! пароль и имя пользователя должны  совпадать в сервисах web и db
- из командной строки запустить: docker-compose -p mathteacher/bot_project2_web up -d
- приложение будет запущено и доступно по адресу http://127.0.0.1:5000/ 

 
**3. Локальная сборка и запуск приложения
**
- Установить GitHub Desctop https://docs.github.com/en/desktop либо его аналог для CLI
- установить Python версии > = 3.9
- Создать в виртуальном окружении локальную копию репозитория с приложением
  git clone https://github.com/anna-khodyka/draft-project-2.git
- Установить все python пакеты, от которых зависит приложение:
  pip install -r requirements.txt	
- Создать переменные окружения
  FLASK_APP main.py:init_app.py()
  DB_PASSWORD пароль_к_базе_данных_постргес
  DB_USER пользователь_базы_данных_постргес
  DB_HOST адрес_сервера_постгрес
  DATA_BASE база_данных_постгрес
- Запустить базу данных PostgreSQL, например при помощи docker compose
- Запустить приложение: flask run -p PORT - h  localhost			
