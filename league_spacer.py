import time

import undetected_chromedriver.v2 as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from ProcessPool import NoDaemonProcessPool


def get_list_total(url):
    acc_list = []
    with open('works/spacer.txt', 'r', encoding='utf-8') as file:
        for idx, val in enumerate(file):
            i = idx + 1
            phone = val.split(':')[0]
            password = val.split(':')[1].replace('\n', '')
            acc = {'phone': phone,
                   'password': password,
                   'number_process': i,
                   'url': url
                   }
            acc_list.append(acc)
    return acc_list


def open_ligue(acc_list):
    sleep = acc_list['number_process'] - 1
    password = acc_list['password']
    phone = acc_list['phone']
    url = acc_list['url']
    sleep = sleep * 25
    time.sleep(sleep)
    options = uc.ChromeOptions()
    options.add_argument('--incognito')
    options.add_argument('--no-first-run --no-service-autorun --password-store=basic')
    options.add_argument('--disable-gpu')
    options.add_argument("--window-size=400,901")
    driver = uc.Chrome(options=options)
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    driver.get('https://m.ligastavok.ru')
    login = WebDriverWait(driver, 30, 0.1, ).until(
        EC.presence_of_element_located(
            (By.XPATH, '/html/body/div[1]/div[1]/div[2]/header/div[3]/div/a[1]')))
    login.click()
    time.sleep(1)
    phone_input = driver.find_element(By.XPATH,
                                      '/html/body/div[1]/div[1]/div[4]/div[1]/div[2]/form/div[1]/input')
    time.sleep(1)
    phone_input.click()
    phone_input.send_keys(phone)
    password_input = driver.find_element(By.XPATH,
                                         '/html/body/div[1]/div[1]/div[4]/div[1]/div[2]/form/div[2]/input')

    password_input.send_keys(password)

    driver.find_element(By.XPATH,
                        '/html/body/div[1]/div[1]/div[4]/div[1]/div[2]/form/button').click()
    time.sleep(8)
    driver.get('https://m.ligastavok.ru/' + url)
    time.sleep(3600)


def start_spacer(url):
    acc_list = get_list_total(url)
    p = NoDaemonProcessPool(processes=len((acc_list)))
    p.map(open_ligue, acc_list)
