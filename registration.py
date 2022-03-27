import json
import logging
import random
import time
import warnings
from datetime import datetime

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from ProcessPool import NoDaemonProcessPool
from chromedriver.locate import DRIVER_DIR
from dolphin import start_dolphin_automation, get_profile_id
from exeptions import AccountError, AccountErrorBettery
from vac_sms_api import get_sms_code, bad_number, get_phone, again_sms

warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')

error_inn = 0


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
    phone_input = WebDriverWait(driver, 120, 0.1).until(
        EC.presence_of_element_located((By.XPATH,
                                        '/html/body/div[2]/div/div[4]/div[1]/div/div/div[2]/div/div[1]/form/div/div/div[1]/div[1]/div[1]/div[1]/label/div[2]/input')))
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
        time.sleep(1)
    while True:
        if check is False:
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

    # Регистрация этап 2
    surnames_input = WebDriverWait(driver, 120, 0.1).until(
        EC.presence_of_element_located((By.XPATH,
                                        '/html/body/div[2]/div/div[5]/div[1]/div/div/div[2]/section/div[1]/div[2]/section/div/div/div[2]/div[1]/div[2]/div[1]/label/div[2]/input')))

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
            raise AccountErrorBettery(f"Аккаунт №{acc['number_process']} уже был зарегестрирован Betery")
    try:
        driver.close()
        driver.quit()
        driver.dispose()
    except:
        pass
    return account


def registration_liga(acc):
    logging.info(f'Начало регистрации liga stavok аккаунт №{acc["number_process"]}')
    """Регистрация Лига ставок."""
    global code
    again_sms(acc['idNum'])
    profile_id = get_profile_id()
    port = start_dolphin_automation(int(profile_id))
    phone_number = acc['phone_number']
    idNum = acc['idNum']
    date_of_birth = acc['date_of_birth']
    password = acc['password']
    name = acc['name']
    surnames = acc['surnames']

    options = Options()
    options.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
    driver = webdriver.Chrome(options=options, executable_path=f"{DRIVER_DIR}\chromedriver")
    driver.get('https://m.ligastavok.ru/registration')
    driver.set_window_size(400, 901)
    time.sleep(2)

    WebDriverWait(driver, 120, 0.1, ).until(
        EC.presence_of_element_located((By.CSS_SELECTOR,
                                        '#app > div.application-c8e1da.application_disable-nav-609602 > div.registration-c64991 > div > form > div.registration__cell-558e5d > div > input')))
    phone_input = driver.find_element(By.XPATH,
                                      '/html/body/div[1]/div[1]/div[4]/div/form/div[1]/div/input')
    phone_input.click()
    time.sleep(1)
    phone_input = driver.find_element(By.XPATH,
                                      '/html/body/div[1]/div[1]/div[4]/div/form/div[1]/div/input')
    phone_input.send_keys(phone_number[1:])
    # phone = ''
    # while phone == '':
    #     phone_input = driver.find_element(By.CSS_SELECTOR,
    #                                       '#app > div.application-c8e1da.application_disable-nav-609602 > div.registration-c64991 > div > form > div.registration__cell-558e5d > div > input')
    #     time.sleep(1)
    #     phone_input.send_keys(phone_number[1:])
    #     phone_cheak = driver.find_element(By.CSS_SELECTOR,
    #                                       '#app > div.application-c8e1da.application_disable-nav-609602 > div.registration-c64991 > div > form > div.registration__cell-558e5d > div > input')
    #     phone = phone_cheak.get_attribute("value")
    time.sleep(1)
    code_proceed = driver.find_element(By.XPATH,
                                       '/html/body/div[1]/div[1]/div[4]/div/form/div[1]/button')
    driver.execute_script("arguments[0].click();", code_proceed)

    while True:
        code = get_sms_code(idNum)['smsCode']
        if code is not None:
            break
        time.sleep(1)

    code_input = driver.find_element(By.XPATH,
                                     '/html/body/div[1]/div[1]/div[4]/div/form/div[3]/div/input')
    code_input.send_keys(code)
    time.sleep(2)
    proceed = driver.find_element(By.XPATH,
                                  '/html/body/div[1]/div[1]/div[4]/div/form/div[5]/button')
    driver.execute_script("arguments[0].click();", proceed)

    time.sleep(5)
    date_input = driver.find_element(By.XPATH,
                                     '/html/body/div[1]/div[1]/div[4]/div/form/div[1]/div/input')
    date_input.click()
    date_input.send_keys(date_of_birth)
    # country_input = driver.find_element(By.CSS_SELECTOR,
    #                                     '#content > div > div > div > form > div:nth-child(2) > div > div.better-inputs__auto-complete-container-040f90 > input')
    # country_input.send_keys('Россия')
    password_input = driver.find_element(By.XPATH,
                                         '/html/body/div[1]/div[1]/div[4]/div/form/div[3]/div[1]/input')
    password_input.click()
    password_input.send_keys(password)
    time.sleep(1)

    try:
        regestr = driver.find_element(By.XPATH,
                                      '/html/body/div[1]/div[1]/div[4]/div/form/div[6]/button')
        driver.execute_script("arguments[0].click();", regestr)
    except:
        time.sleep(1)
        regestr = driver.find_element(By.XPATH,
                                      '/html/body/div[1]/div[1]/div[4]/div/form/div[6]/button')
        driver.execute_script("arguments[0].click();", regestr)
    now = datetime.now()
    verify = False
    while True:
        next = datetime.now() - now
        if next.seconds > 70:
            break
        soup = BeautifulSoup(driver.page_source, 'lxml')
        complete = soup.find_all("div",
                                 class_="notification-6593a1 notification_info-f737e8 simple-ident-limits-info-339d4c")
        if complete:
            verify = True
            break

    try:
        driver.close()
        driver.quit()
        driver.dispose()
    except:
        pass
    if verify is True:
        string = f"{phone_number[1:]}:{password}:{profile_id}\n"
        with open('works/total.txt', 'a', encoding="UTF8") as f:
            f.write(string)
    else:
        raise AccountError(f"Аккаунт №{acc['number_process']} уже был зарегестрирован Liga, {name} {surnames}")


def test_write(acc):
    account = {"acc2": {'phone_number': acc['phone_number'],
                        'idNum': acc['idNum'],
                        'date_of_birth': acc['date_of_birth'],
                        'password': acc['password']}

               }
    b = json.load(open('result.json'))
    b.update(account)
    json.dump(b, open('result.json', 'w'))


def start(acc):
    account = registration(acc)
    registration_liga(account)


def start_registration(data):
    p = NoDaemonProcessPool(processes=2)
    p.map(start, data)
