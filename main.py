import json
import logging
import multiprocessing
import os
import random
import re
import time
from datetime import datetime
from multiprocessing.pool import Pool
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


def get_phone(count):
    """Покупка номера на VAC sms."""
    if int(count) > 1:
        time.sleep(2)
    if not check_balance():
        raise Exception("Не хватает дененг на Vac-Sms")
    params = {
        'apiKey': VAC_TOKEN,
        'service': 'cp',
        'country': 'ru',
        'operator': 'mtt'
    }
    phone_count = requests.get('https://vak-sms.com/api/getCountNumber/', params=params)
    value = phone_count.json()
    if int(value['cp']) < 0:
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
    print(f"Номер {idNum} был отменен")
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
    acc = parse_txt_acc()
    global code
    idNum = phone['idNum']
    phone_number = str(phone['tel'])
    date_of_birth = acc['date_of_birth']
    password = password_generate()
    name = acc['name']
    surnames = acc['surnames']
    patronymic = acc['patronymic']
    passport = acc['passport']
    inn = acc['inn']
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options, executable_path=f"{DRIVER_DIR}\chromedriver")
    driver.get('https://www.bettery.ru/account/registration/')
    time.sleep(5)
    phone_input = driver.find_element(By.XPATH,
                                      '/html/body/div[2]/div/div[4]/div[1]/div/div/div[2]/div/div[1]/form/div/div/div[1]/div[1]/div[1]/div[1]/label/div[2]/input')
    phone_input.send_keys(phone_number[2:])
    date_input = driver.find_element(By.XPATH,
                                     '/html/body/div[2]/div/div[4]/div[1]/div/div/div[2]/div/div[1]/form/div/div/div[1]/div[1]/div[1]/div[2]/label/div[2]/input')
    date_input.click()
    date_input.send_keys(date_of_birth)
    password_input = driver.find_element(By.XPATH,
                                         '/html/body/div[2]/div/div[4]/div[1]/div/div/div[2]/div/div[1]/form/div/div/div[1]/div[1]/div[1]/div[3]/label/div[2]/input')
    password_input.send_keys(password)
    driver.find_element(By.XPATH,
                        '/html/body/div[2]/div/div[4]/div[1]/div/div/div[2]/div/div[1]/form/div/div/div[1]/div[2]/div/div/input').click()
    driver.find_element(By.XPATH,
                        '/html/body/div[2]/div/div[4]/div[1]/div/div/div[2]/div/div[1]/form/div/div/div[2]/div').click()
    now = datetime.now()
    check = False
    click = False
    while True:
        next = datetime.now() - now
        if next.seconds >= 60 and click is False:
            driver.find_element(By.XPATH,
                                '/html/body/div[2]/div/div[4]/div[1]/div/div/div[2]/div/div[1]/form/div/div/div[2]/div[1]/div[2]/div[2]/a/div/span').click()
            click = True
        if next.seconds >= 120:
            break
        code = get_sms_code(idNum)['smsCode']
        if code is None:
            time.sleep(3)
        else:
            check = True
            break
    time.sleep(5)
    while True:
        if not check:
            bad_number(idNum)
            phone = get_phone(count='1')
            idNum = phone['idNum']
            phone_number = str(phone['tel'])
            driver.find_element(By.XPATH,
                                '/html/body/div[2]/div/div[4]/div[1]/div/div/div[2]/div/div[1]/form/div/div/div[2]/div[1]/div[2]/div[1]/a/div/span').click()
            time.sleep(2)
            driver.refresh()
            phone_input = driver.find_element(By.XPATH,
                                              '/html/body/div[2]/div/div[4]/div[1]/div/div/div[2]/div/div[1]/form/div/div/div[1]/div[1]/div[1]/div[1]/label/div[2]/input')
            phone_input.send_keys(phone_number[2:])

            date_input = driver.find_element(By.XPATH,
                                             '/html/body/div[2]/div/div[4]/div[1]/div/div/div[2]/div/div[1]/form/div/div/div[1]/div[1]/div[1]/div[2]/label/div[2]/input')
            date_input.click()
            date_input.send_keys(date_of_birth)
            password_input = driver.find_element(By.XPATH,
                                                 '/html/body/div[2]/div/div[4]/div[1]/div/div/div[2]/div/div[1]/form/div/div/div[1]/div[1]/div[1]/div[3]/label/div[2]/input')
            password_input.send_keys(password)
            driver.find_element(By.XPATH,
                                '/html/body/div[2]/div/div[4]/div[1]/div/div/div[2]/div/div[1]/form/div/div/div[1]/div[2]/div/div/input').click()

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
    name_input = driver.find_element(By.XPATH,
                                     '/html/body/div[2]/div/div[5]/div[1]/div/div/div[2]/section/div[1]/div[2]/section/div/div/div[2]/div[1]/div[2]/div[2]/label/div[2]/input')
    name_input.click()
    name_input.send_keys(name)
    patronymic_input = driver.find_element(By.XPATH,
                                           '/html/body/div[2]/div/div[5]/div[1]/div/div/div[2]/section/div[1]/div[2]/section/div/div/div[2]/div[1]/div[2]/div[3]/label[2]/div[2]/input')
    patronymic_input.click()
    patronymic_input.send_keys(patronymic)
    passport_input = driver.find_element(By.XPATH,
                                         '/html/body/div[2]/div/div[5]/div[1]/div/div/div[2]/section/div[1]/div[2]/section/div/div/div[2]/div[1]/div[2]/div[5]/label/div[2]/input')
    passport_input.click()
    passport_input.send_keys(passport)
    inn_input = driver.find_element(By.XPATH,
                                    '/html/body/div[2]/div/div[5]/div[1]/div/div/div[2]/section/div[1]/div[2]/section/div/div/div[2]/div[1]/div[2]/div[6]/div[2]/div/label/div[1]/input')
    inn_input.click()
    inn_input.send_keys(inn)
    time.sleep(1)
    if inn == '':
        inn = suggest_inn(surname=surnames, name=name, patronymic=patronymic, birthdate=date_of_birth,
                          docnumber=passport, doctype='21')
        inn_input.click()
        inn_input.clear()
        inn_input.send_keys(inn)

    driver.find_element(By.XPATH,
                        '/html/body/div[2]/div/div[5]/div[1]/div/div/div[2]/section/div[1]/div[2]/section/div/div/div[2]/div[1]/div[2]/div[7]/div/div[1]/div').click()
    time.sleep(1)
    driver.find_element(By.XPATH,
                        '/html/body/div[2]/div/div[5]/div[1]/div/div/div[2]/section/div[1]/div[2]/section/div/div/div[2]/div[1]/div[3]/div[1]/a/div/span').click()
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

    options = uc.ChromeOptions()
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

    while True:
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
    date_input = driver.find_element(By.XPATH,
                                     '/html/body/div[1]/div[3]/div/div/div/div/form/div[1]/div[1]/input')
    date_input.click()
    date_input.send_keys(date_of_birth)
    password_input = driver.find_element(By.XPATH,
                                         '/html/body/div[1]/div[3]/div/div/div/div/form/div[3]/div[1]/input')
    password_input.send_keys(password)
    country_input = driver.find_element(By.XPATH,
                                        '/html/body/div[1]/div[3]/div/div/div/div/form/div[2]/div/div[2]/input')
    country_input.send_keys('Россия')
    driver.find_element(By.XPATH,
                        '/html/body/div[1]/div[3]/div/div/div/div/form/div[6]/button/span').click()
    now = datetime.now()
    # verif = False
    while True:
        next = datetime.now() - now
        if next.seconds == 500:
            break
        soup = BeautifulSoup(driver.page_source, 'lxml')
        complete = soup.find_all("div", class_="simple-id-notification-a011c3")
        if complete:
            # verif = True
            break
    now = datetime.now().strftime("%d/%m/%y %I:%M:%S")
    string = f"Номер: {phone_number},пароль: {password}, id номера VAC sms : {idNum}, Регистрация без колеса, время: {now}\n"
    with open('total.txt', 'a', encoding="UTF8") as f:
        f.write(string)
    # if verif is True:
    #     time.sleep(120)
    #     driver.get('https://www.ligastavok.ru/promo/fortune')
    #     time.sleep(5)
    #     d = driver.find_element(By.TAG_NAME, 'iframe')
    #     driver.switch_to.frame(d)
    #     driver.find_element(By.XPATH, '/html/body/div[1]/div[1]/div[2]/div[1]/button').click()
    #     time.sleep(15)
    #     driver.close()
    #     now = datetime.now().strftime("%d/%m/%y %I:%M:%S")
    #     string = f"Номер: {phone_number},пароль: {password}, id номера VAC sms : {idNum}, время: {now}\n"
    #     with open('total.txt', 'a', encoding="UTF8") as f:
    #         f.write(string)
    # else:
    #     now = datetime.now().strftime("%d/%m/%y %I:%M:%S")
    #     string = f"Номер: {phone_number},пароль: {password}, id номера VAC sms : {idNum}. Регистрация без колеса, время: {now}\n"
    #     with open('total.txt', 'a', encoding="UTF8") as f:
    #         f.write(string)


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
    """Получаем инн."""
    docnumber = f'{docnumber[:2]} {docnumber[2:4]} {docnumber[4:10]}'
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
    inn = resp.json()
    return inn['inn']


def test_2():
    response = suggest_inn(
        surname="Шишкина",
        name="Яна",
        patronymic="Александровна",
        birthdate="22.07.1988",
        doctype="21",
        docnumber="3215610309",
    )
    print(response)


def test_write(acc):
    account = {"acc2": {'phone_number': acc['phone_number'],
                        'idNum': acc['idNum'],
                        'date_of_birth': acc['date_of_birth'],
                        'password': acc['password']}

               }
    b = json.load(open('result.json'))
    b.update(account)
    json.dump(b, open('result.json', 'w'))


def parse_txt_acc():
    """Достаем данные из текстовика."""
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
    patronymic = parts[2].replace(',', '')
    date_of_birth = parts[5].replace(',', '')
    passport = ps.replace(' ', '')
    inn = suggest_inn(surnames, name, patronymic, date_of_birth, '21', passport)
    acc = {'date_of_birth': date_of_birth,
           'passport': passport,
           'patronymic': patronymic,
           'name': name,
           'surnames': surnames,
           'inn': inn
           }
    return acc


def start(count):
    phone = get_phone(count)
    account = registration(phone)
    registration_liga(account)


class NoDaemonProcess(multiprocessing.Process):
    # make 'daemon' attribute always return False
    @property
    def daemon(self):
        return False

    @daemon.setter
    def daemon(self, val):
        pass


class NoDaemonProcessPool(Pool):

    def Process(self, *args, **kwds):
        proc = super(NoDaemonProcessPool, self).Process(*args, **kwds)
        proc.__class__ = NoDaemonProcess

        return proc


def main():
    count = ['1', '2']
    try:
        p = NoDaemonProcessPool(processes=2)
        p.map(start, count)
    except Exception as error:
        logging.error(error)


if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()
