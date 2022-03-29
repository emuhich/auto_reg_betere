import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from chromedriver.locate import DRIVER_DIR
from dolphin import start_dolphin_automation, login_ligue


def get_list_total(url):
    acc_list = []
    with open('works/spacer.txt', 'r', encoding='utf-8') as file:
        for idx, val in enumerate(file):
            i = idx + 1
            phone = val.split(':')[0]
            password = val.split(':')[1]
            profile_id = val.split(':')[2].replace('\n', '')
            acc = {'phone': phone,
                   'password': password,
                   'number_process': i,
                   'url': url,
                   'profile_id': profile_id
                   }
            acc_list.append(acc)
    return acc_list


def open_ligue(acc_list):
    sleep = acc_list['number_process'] - 1
    password = acc_list['password']
    phone = acc_list['phone']
    url = acc_list['url']
    profile_id = acc_list['profile_id']
    port = start_dolphin_automation(int(profile_id))
    options = Options()
    options.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
    # Change chrome driver path accordingly
    driver = webdriver.Chrome(options=options, executable_path=f"{DRIVER_DIR}\chromedriver")
    driver.set_window_size(400, 901)
    driver.get('https://m.ligastavok.ru')
    in_account = True
    try:
        driver.find_element(By.CSS_SELECTOR,
                            '#app > div.application-c8e1da > div.application__fixed-ae5951 > header > div.block-header__controls-ffdd12 > a.block-header__wallet-5ba961 > div')
    except:
        in_account = False
    if not in_account:
        try:
            driver = login_ligue(driver, phone, password, version=True)
        except:
            driver = login_ligue(driver, phone, password, version=False)
    driver.get('https://m.ligastavok.ru/' + url)


def start_spacer(url):
    acc_list = get_list_total(url)
    for i in acc_list:
        open_ligue(i)

