import os
import random
import time

import requests as requests
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By

from chromedriver.locate import DRIVER_DIR

load_dotenv()

VAC_TOKEN = os.getenv("VAC_SMS_TOKEN")


def get_phone():
    """Покупка номера на VAC sms."""
    if not check_balance():
        raise Exception("Не хватает дененг")
    params = {
        'apiKey': VAC_TOKEN,
        'service': 'cp',
        'country': 'ru',
    }
    phone_count = requests.get('https://vak-sms.com/api/getCountNumber/', params=params)
    count = phone_count.json()
    if int(count['cp']) < 0:
        raise Exception("Кончились номера")
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
    print(password)


def registration(phone):
    """Регистрация bettery."""
    # Регистрация этап 1
    global code
    idNum = phone['idNum']
    phone_number = str(phone['tel'])
    date_of_birth = '03.03.1975'
    password = '123987Egor'
    name = 'Любовь'
    surnames = 'Карпова'
    patronymic = 'Николаевна'
    passport = '9219 713041'
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
    time.sleep(60)
    counter = 0
    check = False
    while True:
        if counter == 10:
            break
        code = get_sms_code(idNum)['smsCode']
        if code is None:
            counter += 1
            time.sleep(32)
        else:
            check = True
            break
    # Регистрация этап 2
    if check:
        code_input = driver.find_element(By.XPATH,
                                             '/html/body/div[2]/div/div[4]/div[1]/div/div/div[2]/div/div[1]/form/div/div/div[2]/div[1]/div[1]/div/label/div[2]/input')
        code_input.send_keys(code)
        time.sleep(2)
        driver.find_element(By.XPATH,
                            '/html/body/div[2]/div/div[4]/div[1]/div/div/div[2]/div/div[1]/form/div/div/div[2]/div[2]/div/button/div/span').click()
        time.sleep(4)
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
        time.sleep(7)
        driver.find_element(By.XPATH,
                            '/html/body/div[2]/div/div[5]/div[1]/div/div/div[2]/section/div[1]/div[2]/section/div/div/div[2]/div[1]/div[2]/div[6]/div[2]/div/div').click()
        time.sleep(1)
        driver.find_element(By.XPATH,
                            '/html/body/div[2]/div/div[5]/div[1]/div/div/div[2]/section/div[1]/div[2]/section/div/div/div[2]/div[1]/div[2]/div[7]/div/div[1]/div').click()
        time.sleep(2)
        driver.find_element(By.XPATH,
                            '/html/body/div[2]/div/div[5]/div[1]/div/div/div[2]/section/div[1]/div[2]/section/div/div/div[2]/div[1]/div[3]/div[1]/a/div/span').click()
        time.sleep(40)
        if driver.find_element(By.XPATH,
                            '/html/body/div[2]/div/div[3]/div/div/div/div[3]/div/a/div/span'):
            return f'{phone_number}, {password}, {idNum}'


def main():
    phone = get_phone()
    account = registration(phone)
    print(account)


if __name__ == '__main__':
    main()
