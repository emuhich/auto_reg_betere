# Программа для автоматической регистрации на сайте

![Selenium](https://img.shields.io/badge/-selenium-%43B02A?style=for-the-badge&logo=selenium&logoColor=white)
![Postman](https://img.shields.io/badge/Postman-FF6C37?style=for-the-badge&logo=postman&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)

## Описание проекта:
Программа использоет библиотеку Selenium и Dolphin Anty API для автоматичекской регистрации на сайте букмейкерский контор. Так же используется API сервиса VAC SMS для аренды номеров, все настройки можно задать в файле settings.ini.
Интерфейс и работа с программой ведется через консольное окно.
Так же проект компилируется в exe файл при помощи библотеки -  auto-py-to-exe.

## Запуск проекта

Клонируйте репозиторий: 
 
``` 
git clone https://github.com/emuhich/auto_reg_betere.git
``` 

Перейдите в папку проекта в командной строке:

``` 
cd auto_reg_betere
``` 

Создайте и активируйте виртуальное окружение:

``` 
python -m venv venv
``` 
``` 
venv/Scripts/activate
``` 

Установите зависимости из файла *requirements.txt*: 
 
``` 
pip install -r requirements.txt
``` 

Запустите сервер:
``` 
python main.py
``` 
