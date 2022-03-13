import json
import logging
import os
import random
import re
import time
from datetime import datetime

import requests as requests
import undetected_chromedriver.v2 as uc
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By

from ProcessPool import NoDaemonProcessPool
from auto_wheel import wheel, get_count_total
from chromedriver.locate import DRIVER_DIR
from exeptions import AccountError, NoString, NoMoney
from league_spacer import start_spacer

load_dotenv()

VAC_TOKEN = os.getenv("VAC_SMS_TOKEN")
error_inn = 0


def get_phone():
    """Покупка номера на VAC sms."""
    params = {
        'apiKey': VAC_TOKEN,
        'service': 'cp',
        'country': 'ru',
        'operator': 'mtt',
        'softId': 1025
    }
    phone_count = requests.get('https://vak-sms.com/api/getCountNumber/', params=params)
    value = phone_count.json()
    if int(value['cp']) < 20:
        params = {
            'apiKey': VAC_TOKEN,
            'service': 'cp',
            'country': 'ru',
            'operator': 'mtt',
            'rent': True,
            'softId': 1025
        }
    phone = requests.get('https://vak-sms.com/api/getNumber/', params=params)
    return phone.json()


def check_balance(count):
    """Проверка баланса VAC sms."""
    summ = 10
    params = {
        'apiKey': VAC_TOKEN,
        'service': 'cp',
        'country': 'ru',
        'operator': 'mtt'
    }
    phone_count = requests.get('https://vak-sms.com/api/getCountNumber/', params=params)
    value = phone_count.json()
    if int(value['cp']) < 20:
        summ = 25
    params = {
        'apiKey': VAC_TOKEN,
    }
    balance = requests.get('https://vak-sms.com/api/getBalance', params=params).json()
    if int(balance['balance']) < summ * count:
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
    chars = 'abcdefghijklnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
    length = 8
    password = ''
    for i in range(length):
        password += random.choice(chars)
    password += str(random.randrange(0, 9))
    password += 'Z'
    return password


def registration(acc):
    logging.info(f'Начало регистрации bettery аккаунт №{acc["number_process"]}')
    """Регистрация bettery."""
    # Регистрация этап 1
    global code
    date_of_birth = acc['date_of_birth']
    password = password_generate()
    name = acc['name']
    surnames = acc['surnames']
    patronymic = acc['patronymic']
    passport = acc['passport']
    inn = acc['inn']
    idNum = acc['idNum']
    phone_number = str(acc['tel'])
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-gpu')
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_experimental_option(
        'prefs',
        {
            'profile.managed_default_content_settings.images': 2,
            'profile.managed_default_content_settings.mixed_script': 2,
            'profile.managed_default_content_settings.media_stream': 2,
            'profile.managed_default_content_settings.stylesheets': 2
        }
    )
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
        if code is not None:
            check = True
            break
        time.sleep(2)
    while True:
        if not check:
            bad_number(idNum)
            phone = get_phone()
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
                if code is not None:
                    check = True
                    break
                time.sleep(1)
        break

    code_input = driver.find_element(By.XPATH,
                                     '/html/body/div[2]/div/div[4]/div[1]/div/div/div[2]/div/div[1]/form/div/div/div[2]/div[1]/div[1]/div/label/div[2]/input')
    code_input.send_keys(code)
    time.sleep(2)
    driver.find_element(By.XPATH,
                        '/html/body/div[2]/div/div[4]/div[1]/div/div/div[2]/div/div[1]/form/div/div/div[2]/div[2]/div/button/div/span').click()
    time.sleep(6)

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
    time.sleep(2)
    while True:
        proceed = driver.find_element(By.XPATH,
                                      '/html/body/div[2]/div/div[5]/div[1]/div/div/div[2]/section/div[1]/div[2]/section/div/div/div[2]/div[1]/div[3]/div[1]/a/div/span')
        driver.execute_script("arguments[0].click();", proceed)
        time.sleep(1)
        soup = BeautifulSoup(driver.page_source, 'lxml')
        ident = soup.find_all("div", class_="markdown _new_design verification__check-data-md--2UWzu")
        if ident:
            break

    account = {
        'phone_number': phone_number,
        'idNum': idNum,
        'date_of_birth': date_of_birth,
        'password': password,
        'name': name,
        'surnames': surnames,
        'patronymic': patronymic,
        'passport': passport,
        'number_process': acc['number_process']

    }
    while True:
        soup = BeautifulSoup(driver.page_source, 'lxml')
        complete = soup.find_all("div", class_="verification__complete--q2ezc")
        if complete:
            break
        error = soup.find_all("div", class_="verification__error--3hIEg")
        if error:
            time.sleep(3)
            driver.close()
            registration_liga(account)
            raise Exception(f"Аккаунт №{acc['number_process']} уже был зарегестрирован Betery")
    driver.close()
    return account


def registration_liga(acc):
    logging.info(f'Начало регистрации liga stavok аккаунт №{acc["number_process"]}')
    """Регистрация Лига ставок."""
    global code
    again_sms(acc['idNum'])
    phone_number = acc['phone_number']
    idNum = acc['idNum']
    date_of_birth = acc['date_of_birth']
    password = acc['password']
    name = acc['name']
    surnames = acc['surnames']

    options = uc.ChromeOptions()
    options.add_argument('--incognito')
    options.add_argument('--no-first-run --no-service-autorun --password-store=basic')
    options.add_argument('--disable-gpu')
    driver = uc.Chrome(options=options)
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    driver.get('https://www.ligastavok.ru/registration')
    time.sleep(4)
    phone_input = driver.find_element(By.CSS_SELECTOR,
                                      '#content > div > div > div > form > div:nth-child(1) > div > input')
    time.sleep(1)
    phone_input.send_keys(phone_number[1:])
    time.sleep(1)
    code_proceed = driver.find_element(By.CSS_SELECTOR,
                                       '#content > div > div > div > form > div:nth-child(2) > button > span')
    driver.execute_script("arguments[0].click();", code_proceed)

    while True:
        code = get_sms_code(idNum)['smsCode']
        if code is not None:
            break
        time.sleep(1)

    code_input = driver.find_element(By.CSS_SELECTOR,
                                     '#content > div > div > div > form > div:nth-child(2) > div > input')
    code_input.send_keys(code)
    time.sleep(2)
    proceed = driver.find_element(By.CSS_SELECTOR,
                                  '#content > div > div > div > form > div.registration__cell_full-width-0cae2c.registration__button-container-ddd816 > button')
    driver.execute_script("arguments[0].click();", proceed)

    time.sleep(5)
    date_input = driver.find_element(By.CSS_SELECTOR,
                                     '#content > div > div > div > form > div:nth-child(1) > div:nth-child(1) > input')
    date_input.click()
    date_input.send_keys(date_of_birth)
    country_input = driver.find_element(By.CSS_SELECTOR,
                                        '#content > div > div > div > form > div:nth-child(2) > div > div.better-inputs__auto-complete-container-040f90 > input')
    country_input.send_keys('Россия')
    password_input = driver.find_element(By.CSS_SELECTOR,
                                         '#content > div > div > div > form > div:nth-child(3) > div.better-inputs__password-1460a4 > input')
    password_input.click()
    password_input.send_keys(password)
    time.sleep(1)

    try:
        regestr = driver.find_element(By.XPATH,
                                      '/html/body/div[1]/div[3]/div/div/div/div/form/div[6]/button/span')
        driver.execute_script("arguments[0].click();", regestr)
    except :
        time.sleep(1)
        regestr = driver.find_element(By.XPATH,
                                      '/html/body/div[1]/div[3]/div/div/div/div/form/div[6]/button/span')
        driver.execute_script("arguments[0].click();", regestr)
    now = datetime.now()
    verify = False
    while True:
        next = datetime.now() - now
        if next.seconds > 70:
            break
        soup = BeautifulSoup(driver.page_source, 'lxml')
        complete = soup.find_all("div", class_="simple-id-notification-a011c3")
        if complete:
            verify = True
            break

    driver.close()
    if verify is True:
        string = f"{phone_number[1:]}:{password}\n"
        with open('total.txt', 'a', encoding="UTF8") as f:
            f.write(string)
    else:
        raise AccountError(f"Аккаунт №{acc['number_process']} уже был зарегестрирован Liga, {name} {surnames}")


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
    try:
        resp = requests.post(url=url, data=data)
        resp.raise_for_status()
        inn = resp.json()
        inn = inn['inn']
    except Exception:
        logging.debug("Ошибка при выдачи инн")
        inn = False
        return inn
    return inn


def test_write(acc):
    account = {"acc2": {'phone_number': acc['phone_number'],
                        'idNum': acc['idNum'],
                        'date_of_birth': acc['date_of_birth'],
                        'password': acc['password']}

               }
    b = json.load(open('result.json'))
    b.update(account)
    json.dump(b, open('result.json', 'w'))


def log():
    file_log = logging.FileHandler('bot_log.log', encoding='utf8')
    console_out = logging.StreamHandler()
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s, %(levelname)s, %(message)s',
        handlers=(file_log, console_out),
    )

    logging.getLogger('undetected_chromedriver').setLevel('CRITICAL')
    logging.getLogger('selenium').setLevel('CRITICAL')
    logging.getLogger('asyncio').setLevel('CRITICAL')
    logging.getLogger('uc').setLevel('CRITICAL')
    logging.getLogger('concurrent').setLevel('CRITICAL')
    logging.getLogger('requests').setLevel('CRITICAL')
    logging.getLogger('socks').setLevel('CRITICAL')
    logging.getLogger('charset_normalizer').setLevel('CRITICAL')
    logging.getLogger('urllib3').setLevel('CRITICAL')
    logging.getLogger('dotenv').setLevel('CRITICAL')


def parse_txt_acc(count):
    """Достаем данные из текстовика."""
    global error_inn
    logging.debug(f'Резервируем номера количество: {count}')
    acc_list = []
    indx = 0
    if not check_balance(count):
        raise NoMoney("Не хватает дененг на Vac-Sms")
    for i in range(0, count):
        indx += 1
        try:
            with open('result.txt', encoding='utf-8') as f:
                lines = f.readlines()

            pattern = re.compile(re.escape(lines[0]))
            with open('result.txt', 'w', encoding='utf-8') as f:
                for line in lines:
                    result = pattern.search(line)
                    if result is None:
                        f.write(line)
        except Exception:
            raise NoString("Кончились строки")

        parts = str.split(' ', )
        ps = str.split(',')[3]

        name = parts[1]
        surnames = parts[0]
        patronymic = parts[2].replace(',', '')
        date_of_birth = parts[5].replace(',', '')
        passport = ps.replace(' ', '')
        inn = suggest_inn(surnames, name, patronymic, date_of_birth, '21', passport)
        if inn is not False:
            phone = get_phone()
            tel = phone['tel']
            idNum = phone['idNum']
            acc = {'date_of_birth': date_of_birth,
                   'passport': passport,
                   'patronymic': patronymic,
                   'name': name,
                   'surnames': surnames,
                   'inn': inn,
                   'tel': tel,
                   'idNum': idNum,
                   'number_process': indx
                   }
            acc_list.append(acc)
        else:
            error_inn += 1

    return acc_list


def start(acc):
    account = registration(acc)
    registration_liga(account)


def generate_list(count):
    data = []
    a = count // 2
    for i in range(0, a):
        data.append('2')
    b = count % 2
    if b > 0:
        data.append('1')
    return data


def get_count_result():
    with open('result.txt', 'r', encoding='utf-8') as file:
        for idx, val in enumerate(file):
            i = idx + 1
        return i


def main():
    global error_inn
    log()

    menu = input(f"Выберите пункт.\n"
                 f"1.Создать аккаунты.\n"
                 f"2.Прокрутить колесо\n"
                 f"3.Проставка\n")
    if menu == '1':
        try:
            string_count = get_count_result()
        except UnboundLocalError:
            logging.error('Пустой файл result.txt')
        else:
            while True:
                count = input(f"Введите количество аккаунтов которое хотите сделать. Не больше {string_count}.")
                if int(count) > string_count:
                    print(f"Вы не можете сделать аккаунтов больше чем строк!!!. Максимально: {string_count}")
                else:
                    break
            spisok = generate_list(int(count))
            acc_error = 0
            other_errors = 0
            logging.debug("Бот начал регестрировать аккаунты")
            for i in spisok:
                try:
                    data = parse_txt_acc(int(i))
                    p = NoDaemonProcessPool(processes=2)
                    p.map(start, data)
                except NoString as error:
                    logging.error(error)
                    break
                except NoMoney as error:
                    logging.error(error)
                    break
                except AccountError as error:
                    logging.error(error)
                    acc_error += 1
                except Exception as error:
                    other_errors += 1
                    logging.error(error)
            ready = get_count_total()
            logging.debug(
                f"Регистрация завершена, зарегистрировано:{ready}/{count}, ошибки инн: {error_inn},"
                f" повторки: {acc_error}, другие ошибки: {other_errors}")
    elif menu == '2':
        logging.debug('Начало прокрутки, все аккаунты беруться из файла total.txt')
        wheel()
    elif menu == '3':
        logging.debug('Начало проставки, все аккаунты беруться из файла spacer.txt')
        url = input('Введите ссылку на матч')
        start_spacer(url)


if __name__ == '__main__':
    main()
