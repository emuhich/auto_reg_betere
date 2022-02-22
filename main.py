import json
import logging
import os
import random
import re
import time
from datetime import datetime
from enum import Enum
from urllib.request import urlopen

import requests as requests
import undetected_chromedriver.v2 as uc
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By

from chromedriver.locate import DRIVER_DIR

load_dotenv()

VAC_TOKEN = os.getenv("VAC_SMS_TOKEN")


def get_phone():
    """Покупка номера на VAC sms."""
    if not check_balance():
        raise Exception("Не хватает дененг на Vac-Sms")
    params = {
        'apiKey': VAC_TOKEN,
        'service': 'cp',
        'country': 'ru',
    }
    phone_count = requests.get('https://vak-sms.com/api/getCountNumber/', params=params)
    count = phone_count.json()
    if int(count['cp']) < 0:
        raise Exception("Кончились номера на Vac-Sms")
    phone = requests.get('https://vak-sms.com/api/getNumber/', params=params)
    return phone.json()


def check_balance():
    """Проверка баланса VAC sms."""
    params = {
        'apiKey': VAC_TOKEN,
    }
    balance = requests.get('https://vak-sms.com/api/getBalance', params=params).json()
    if int(balance['balance']) < 10:
        return False
    return True


def bad_number(idNum):
    """Смена номера."""
    params = {
        'apiKey': VAC_TOKEN,
        'status': 'end',
        'idNum': idNum
    }
    status = requests.get('https://vak-sms.com/api/setStatus/?apiKey={apiKey}&status={status}&idNum={idNum}',
                          params=params).json()
    if status['status'] == 'smsReceived':
        raise Exception("Ошибка отмены номера: на данный номер уже получен код подтверждения, отмена невозможна.")
    elif status['status'] == 'waitSMS':
        raise Exception("на данные номер уже отправлено смс, отмена невозможна. Ожидайте код.")


def again_sms(idNum):
    """Повторное получение смс."""
    params = {
        'apiKey': VAC_TOKEN,
        'status': 'send',
        'idNum': idNum
    }
    status = requests.get('https://vak-sms.com/api/setStatus/?apiKey={apiKey}&status={status}&idNum={idNum}',
                          params=params).json()
    if status['status'] == 'smsReceived':
        raise Exception("Ошибка отмены номера: на данный номер уже получен код подтверждения, отмена невозможна.")
    elif status['status'] == 'waitSMS':
        raise Exception("на данные номер уже отправлено смс, отмена невозможна. Ожидайте код.")


def get_sms_code(idNum):
    """Получение sms кода."""
    params = {
        'apiKey': VAC_TOKEN,
        'idNum': idNum
    }
    code = requests.get('https://vak-sms.com/api/getSmsCode', params=params).json()
    return code


def password_generate():
    """Генератор пароля."""
    chars = '+-/*!&$#?=@<>abcdefghijklnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
    length = 8
    password = ''
    for i in range(length):
        password += random.choice(chars)
    password += str(random.randrange(0, 9))
    return password


def registration(phone):
    """Регистрация bettery."""
    # Регистрация этап 1
    global code
    idNum = phone['idNum']
    phone_number = str(phone['tel'])
    date_of_birth = '13.11.1988'
    password = password_generate()
    name = 'Дарья'
    surnames = 'Лобанова'
    patronymic = 'Андреевна'
    passport = '4608470433'
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options, executable_path=f"{DRIVER_DIR}\chromedriver")
    driver.get('https://www.bettery.ru/account/registration/')
    time.sleep(5)
    phone_input = driver.find_element(By.XPATH,
                                      '/html/body/div[2]/div/div[4]/div[1]/div/div/div[2]/div/div[1]/form/div/div/div[1]/div[1]/div[1]/div[1]/label/div[2]/input')
    phone_input.send_keys(phone_number[2:])
    time.sleep(2)
    date_input = driver.find_element(By.XPATH,
                                     '/html/body/div[2]/div/div[4]/div[1]/div/div/div[2]/div/div[1]/form/div/div/div[1]/div[1]/div[1]/div[2]/label/div[2]/input')
    date_input.click()
    date_input.send_keys(date_of_birth)
    time.sleep(1)
    password_input = driver.find_element(By.XPATH,
                                         '/html/body/div[2]/div/div[4]/div[1]/div/div/div[2]/div/div[1]/form/div/div/div[1]/div[1]/div[1]/div[3]/label/div[2]/input')
    password_input.send_keys(password)
    time.sleep(1)
    driver.find_element(By.XPATH,
                        '/html/body/div[2]/div/div[4]/div[1]/div/div/div[2]/div/div[1]/form/div/div/div[1]/div[2]/div/div/input').click()
    time.sleep(1)
    driver.find_element(By.XPATH,
                        '/html/body/div[2]/div/div[4]/div[1]/div/div/div[2]/div/div[1]/form/div/div/div[2]/div').click()
    now = datetime.now()
    check = False
    while True:
        next = datetime.now() - now
        if next.seconds == 300:
            break
        code = get_sms_code(idNum)['smsCode']
        if code is None:
            time.sleep(3)
        else:
            check = True
            break
    while True:
        if not check:
            bad_number(idNum)
            phone = get_phone()
            idNum = phone['idNum']
            phone_number = str(phone['tel'])
            driver.find_element(By.XPATH,
                                '/html/body/div[2]/div/div[4]/div[1]/div/div/div[2]/div/div[1]/form/div/div/div[2]/div[1]/div[2]/div[1]/a/div/span').click()
            time.sleep(2)
            phone_input = driver.find_element(By.XPATH,
                                              '/html/body/div[2]/div/div[4]/div[1]/div/div/div[2]/div/div[1]/form/div/div/div[1]/div[1]/div[1]/div[1]/label/div[2]/input')
            time.sleep(2)
            phone_input.clear()
            time.sleep(2)
            phone_input.send_keys(phone_number[2:])
            time.sleep(1)
            driver.find_element(By.XPATH,
                                '/html/body/div[2]/div/div[4]/div[1]/div/div/div[2]/div/div[1]/form/div/div/div[2]/div/button/div/span').click()
            now = datetime.now()
            while True:
                next = datetime.now() - now
                if next.seconds == 300:
                    break
                code = get_sms_code(idNum)['smsCode']
                if code is None:
                    time.sleep(3)
                else:
                    check = True
                    break
        break

    code_input = driver.find_element(By.XPATH,
                                     '/html/body/div[2]/div/div[4]/div[1]/div/div/div[2]/div/div[1]/form/div/div/div[2]/div[1]/div[1]/div/label/div[2]/input')
    code_input.send_keys(code)
    time.sleep(2)
    driver.find_element(By.XPATH,
                        '/html/body/div[2]/div/div[4]/div[1]/div/div/div[2]/div/div[1]/form/div/div/div[2]/div[2]/div/button/div/span').click()
    time.sleep(4)

    # Регистрация этап 2
    surnames_input = driver.find_element(By.XPATH,
                                         '/html/body/div[2]/div/div[5]/div[1]/div/div/div[2]/section/div[1]/div[2]/section/div/div/div[2]/div[1]/div[2]/div[1]/label/div[2]/input')
    surnames_input.click()
    surnames_input.send_keys(surnames)
    time.sleep(2)
    name_input = driver.find_element(By.XPATH,
                                     '/html/body/div[2]/div/div[5]/div[1]/div/div/div[2]/section/div[1]/div[2]/section/div/div/div[2]/div[1]/div[2]/div[2]/label/div[2]/input')
    name_input.click()
    name_input.send_keys(name)
    time.sleep(2)
    patronymic_input = driver.find_element(By.XPATH,
                                           '/html/body/div[2]/div/div[5]/div[1]/div/div/div[2]/section/div[1]/div[2]/section/div/div/div[2]/div[1]/div[2]/div[3]/label[2]/div[2]/input')
    patronymic_input.click()
    patronymic_input.send_keys(patronymic)
    time.sleep(2)
    passport_input = driver.find_element(By.XPATH,
                                         '/html/body/div[2]/div/div[5]/div[1]/div/div/div[2]/section/div[1]/div[2]/section/div/div/div[2]/div[1]/div[2]/div[5]/label/div[2]/input')
    passport_input.click()
    passport_input.send_keys(passport)
    time.sleep(3)
    driver.find_element(By.XPATH,
                        '/html/body/div[2]/div/div[5]/div[1]/div/div/div[2]/section/div[1]/div[2]/section/div/div/div[2]/div[1]/div[2]/div[6]/div[2]/div/div').click()
    time.sleep(8)
    driver.find_element(By.XPATH,
                        '/html/body/div[2]/div/div[5]/div[1]/div/div/div[2]/section/div[1]/div[2]/section/div/div/div[2]/div[1]/div[2]/div[7]/div/div[1]/div').click()
    time.sleep(2)
    driver.find_element(By.XPATH,
                        '/html/body/div[2]/div/div[5]/div[1]/div/div/div[2]/section/div[1]/div[2]/section/div/div/div[2]/div[1]/div[3]/div[1]/a/div/span').click()
    time.sleep(2)
    while True:
        soup = BeautifulSoup(driver.page_source, 'lxml')
        complete = soup.find_all("div", class_="verification__complete--q2ezc")
        if complete:
            break
        error = soup.find_all("div", class_="verification__error--3hIEg")
        if error:
            raise Exception("Аккаунт уже был зарегестрирован")

    account = {
        'phone_number': phone_number,
        'idNum': idNum,
        'date_of_birth': date_of_birth,
        'password': password,
        'name': name,
        'surnames': surnames,
        'patronymic': patronymic,
        'passport': passport
    }
    return account


def registration_liga(acc):
    """Регистрация Лига ставок."""
    global code
    again_sms(acc['idNum'])
    phone_number = acc['phone_number']
    idNum = acc['idNum']
    date_of_birth = acc['date_of_birth']
    password = acc['password']

    # ua = UserAgent()
    # us_ag = ua.random
    # chrome_options = webdriver.ChromeOptions()
    # # chrome_options.add_argument('--headless')
    # chrome_options.add_argument('--no-sandbox')
    # chrome_options.add_argument('--window-size=1420,1080')
    # chrome_options.add_argument('--disable-gpu')
    # chrome_options.add_argument(f"user-agent={us_ag}")
    # chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    # chrome_options.add_experimental_option('useAutomationExtension', False)
    # driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=f"{DRIVER_DIR}\chromedriver")
    options = uc.ChromeOptions()
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-first-run')
    options.add_argument('--no-service-autorun')
    options.add_argument('--no-default-browser-check')
    options.add_argument('--password-store=basic')
    options.add_argument('--incognito')
    driver = uc.Chrome(options=options)

    driver.get('https://www.ligastavok.ru/registration')
    time.sleep(5)
    phone_input = driver.find_element(By.XPATH,
                                      '/html/body/div[1]/div[3]/div/div/div/div/form/div[1]/div/input')
    phone_input.send_keys(phone_number[1:])
    time.sleep(1)
    driver.find_element(By.XPATH,
                        '/html/body/div[1]/div[3]/div/div/div/div/form/div[2]/button/span').click()
    now = datetime.now()

    while True:
        next = datetime.now() - now
        if next.seconds == 500:
            break
        code = get_sms_code(idNum)['smsCode']
        if code is None:
            time.sleep(3)
        else:
            break

    code_input = driver.find_element(By.XPATH,
                                     '/html/body/div[1]/div[3]/div/div/div/div/form/div[2]/div/input')
    code_input.send_keys(code)
    time.sleep(2)
    driver.find_element(By.XPATH,
                        '/html/body/div[1]/div[3]/div/div/div/div/form/div[5]/button/span').click()

    time.sleep(5)
    print('Вводим дату')
    date_input = driver.find_element(By.XPATH,
                                     '/html/body/div[1]/div[3]/div/div/div/div/form/div[1]/div[1]/input')
    date_input.click()
    date_input.send_keys(date_of_birth)
    time.sleep(3)
    password_input = driver.find_element(By.XPATH,
                                         '/html/body/div[1]/div[3]/div/div/div/div/form/div[3]/div[1]/input')
    password_input.send_keys(password)
    time.sleep(1)
    country_input = driver.find_element(By.XPATH,
                                        '/html/body/div[1]/div[3]/div/div/div/div/form/div[2]/div/div[2]/input')
    country_input.send_keys('Россия')
    time.sleep(1)
    driver.find_element(By.XPATH,
                        '/html/body/div[1]/div[3]/div/div/div/div/form/div[6]/button/span').click()
    while True:
        soup = BeautifulSoup(driver.page_source, 'lxml')
        complete = soup.find_all("div", class_="simple-id-notification-a011c3")
        if complete:
            break

    while True:
        soup = BeautifulSoup(driver.page_source, 'lxml')
        complete = soup.find_all("div", class_="fortune-popup__wrapper-66fb7c")
        if complete:
            break

    driver.get('https://www.ligastavok.ru/promo/fortune')
    time.sleep(5)
    d = driver.find_element(By.TAG_NAME, 'iframe')
    driver.switch_to.frame(d)
    driver.find_element(By.XPATH, '/html/body/div[1]/div[1]/div[2]/div[1]/button').click()
    time.sleep(15)
    driver.close()
    account = {"acc2": {'phone_number': phone_number,
                        'idNum': idNum,
                        'date_of_birth': date_of_birth,
                        'password': password}

               }
    b = json.load(open('result.json'))
    b.update(account)
    print(b)
    json.dump(b, open('result.json', 'w'))


def chek_nalog():
    """Провера сайта налоговой для получения ИНН."""
    html = urlopen('https://service.nalog.ru/inn.do')
    bs = BeautifulSoup(html.read(), 'lxml')
    result = bs.find_all("div", class_="col-left-75")[0]
    if result:
        pass
        for r in result:
            if r.text == 'Сервис временно недоступен по причине проведения технических работ.':
                raise Exception(
                    "Невозможно запустить скрипт по причине технических работ сайта налогов: https://service.nalog.ru/inn.do")


def suggest_inn(surname, name, patronymic, birthdate, doctype, docnumber):
    url = "https://service.nalog.ru/inn-proc.do"
    data = {
        "fam": surname,
        "nam": name,
        "otch": patronymic,
        "bdate": birthdate,
        "bplace": "",
        "doctype": doctype,
        "docno": docnumber,
        "c": "innMy",
        "captcha": "",
        "captchaToken": "",
    }
    resp = requests.post(url=url, data=data)
    resp.raise_for_status()
    return resp.json()


def test_2():
    response = suggest_inn(
        surname="Воронова",
        name="Нина",
        patronymic="Ивановна",
        birthdate="29.08.1940",
        doctype="21",
        docnumber="40 10 146405",
    )
    print(response)


def test_write(acc):
    # with open('result.json', 'w', encoding="utf-8") as f:
    #     json.dump(acc, f)
    #
    # capitals_json = json.dumps(acc, ensure_ascii=False).encode('utf8')
    #
    # with open("result.json", "w", encoding="utf-8") as my_file:
    #     my_file.write(capitals_json.decode())
    b = json.load(open('result.json'))
    b.update(acc)
    print(b)
    json.dump(b, open('result.json', 'w'))

    # json.dump(b.decode(), open('result.json', 'w'))
    # json.dump(b, open('result.json', 'w'))


def test_open():
    with open('result.txt', encoding='utf-8') as f:
        lines = f.readlines()

    str = lines[0]
    pattern = re.compile(re.escape(str))
    with open('result.txt', 'w', encoding='utf-8') as f:
        for line in lines:
            result = pattern.search(line)
            if result is None:
                f.write(line)

    parts = str.split(' ', )
    ps = str.split(',')[3]

    name = parts[1]
    surnames = parts[0]
    patronymic = parts[2]
    date_of_birth = parts[5]
    passport = ps.replace(' ', '')
    print(f'1: {name}')
    print(f'2: {surnames}')
    print(f'3: {patronymic}')
    print(f'4: {date_of_birth}')
    print(f'5: {passport}')


def main():
    # try:
    #     # chek_nalog()
    #     phone = get_phone()
    #     account = registration(phone)
    #     registration_liga(account)
    # except Exception as error:
    #     logging.error(error)

    # test_2()
    test_open()

    # acc = {"acc2": {'phone_number': '79617973671', 'idNum': '1645543310741953', 'date_of_birth': '15.01.1981',
    #                 'password': '123987Egor',
    #                 'passport': '4606556721'}}
    # test_write(acc)
    # registration_liga(acc)


if __name__ == '__main__':
    main()
