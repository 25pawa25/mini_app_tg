# mini_app_tg

## Чтобы развернуть проект, нужно:

- ### создать в корне файл .env,
- ### скопировать в него содержимое .env.sample
- ### поменять BOT_API_KEY на рабочий
- ### создать виртуальное окружение ```python -m venv venv```
- ### войти в виртуальное окружение ```source venv/bin/activate```
- ### установить зависимости ```pip install -r requirements.txt```
- ### запустить скрипт ```parser.py```
- ### запустить бота ```tg_app.py```

## Команды:

- ### ```/start```: Вывод всех игр
- ### ```/filter 10``` Фильтрация по размеру скидки (в данном случае скидка >=10%)
