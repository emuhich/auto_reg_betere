import json
import logging
import random
import re
import configparser
import time
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent

import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from exeptions import NoString

config = configparser.ConfigParser()
config.read("settings.ini")
TOKEN_DOLPHIN = config["SETTINGS"]["token_dolphin"]


def start_dolphin_automation(profile_id):
    url = f"http://localhost:3001/v1.0/browser_profiles/{profile_id}/start?automation=1"
    response = requests.request("GET", url)
    return response.json()['automation']['port']


def multiple_create_browser(count):
    url = "https://anty-api.com/browser_profiles/mass"
    index = []
    platform = ['windows', 'linux', 'macos']
    cpu = [2, 4, 8, 16]
    memory = [2, 4, 8]
    for i in range(count):
        s = {
            "name": f"test{i + 1}",
            "tags": [
                f"test{i + 1}"
            ],
            "platform": random.choice(platform),
            "cpu": {
                "mode": "manual",
                "value": random.choice(cpu),
            },
            "memory": {
                "mode": "manual",
                "value": random.choice(memory),
            },
            "mainWebsite": "",
            "notes": {
                "content": None,
                "color": "blue",
                "style": "text",
                "icon": "success"
            },
            "useragent": {
                "mode": "manual",
                "value": random_ua()
            },
            "proxy": None,
            "statusId": 0,
            "doNotTrack": False
        }
        index.append(s)
    payload = json.dumps({
        "common": {
            "browserType": "anty",
            "webrtc": {
                "mode": "altered",
                "ipAddress": None
            },
            "canvas": {
                "mode": "real"
            },
            "webgl": {
                "mode": "real"
            },
            "webglInfo": {
                "mode": "real",
            },
            "geolocation": {
                "mode": "auto",
                "latitude": None,
                "longitude": None
            },
            "timezone": {
                "mode": "auto",
                "value": None
            },
            "locale": {
                "mode": "manual",
                "value": 'ru_RU'
            }
        },
        "items": index
    })
    headers = {
        'Authorization': 'Bearer ' + TOKEN_DOLPHIN,
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    if not response.json()['success']:
        logging.error("Ошибка при создании профилей")
        raise Exception("Ошибка при создании профилей")
    return response.json()['ids']


def random_ua():
    ua = UserAgent()
    user = ua.chrome
    version = user.split('/')[3]
    version = version.split(' ')[0]
    user = user.replace(version, '99.0.4844.51')
    return user


def get_profile_id():
    try:
        with open('works/dolphin.txt', encoding='utf-8') as f:
            lines = f.readlines()
        profile_id = lines[0]
        pattern = re.compile(re.escape(profile_id))
        with open('works/dolphin.txt', 'w', encoding='utf-8') as f:
            for line in lines:
                result = pattern.search(line)
                if result is None:
                    f.write(line)
    except Exception:
        raise NoString("Кончились профиля в dolphin.txt")
    return profile_id


def rename_profile(phone, password, profile_id):
    url = f"https://anty-api.com/browser_profiles/{int(profile_id)}"

    payload = json.dumps({
        "name": f"{phone[1:]}:{password}",
    })

    headers = {
        'Authorization': 'Bearer ' + TOKEN_DOLPHIN,
        'Content-Type': 'application/json'
    }

    requests.request("PATCH", url, headers=headers, data=payload)


def refactoring_profile(profile_id, wheel):
    url = f"https://anty-api.com/browser_profiles/{int(profile_id)}"
    if wheel:
        payload = json.dumps({
            "notes": {
                "icon": "success",
                "color": "green",
                "style": 'text',
                'content': '<p>Прокручено</p>'
            }
        })
    else:
        payload = json.dumps({
            "notes": {
                "icon": "error",
                "color": "red",
                "style": 'text',
                'content': '<p>Ошибка прокрутки</p>'
            }
        })

    headers = {
        'Authorization': 'Bearer ' + TOKEN_DOLPHIN,
        'Content-Type': 'application/json'
    }

    requests.request("PATCH", url, headers=headers, data=payload)


def login_ligue(driver, phone, password, version):
    if version:
        login = WebDriverWait(driver, 10, 0.1, ).until(
            EC.presence_of_element_located(
                (By.XPATH, '/html/body/div[1]/div[1]/div[1]/header/div[3]/div/a[1]')))

        login.click()
        time.sleep(1)
        phone_input = driver.find_element(By.XPATH,
                                          '/html/body/div[1]/div[1]/div[3]/div[1]/div[2]/form/div[1]/input')
        time.sleep(1)
        phone_input.click()
        phone_input.send_keys(phone)
        password_input = driver.find_element(By.XPATH,
                                             '/html/body/div[1]/div[1]/div[3]/div[1]/div[2]/form/div[2]/input')

        password_input.send_keys(password)

        driver.find_element(By.XPATH,
                            '/html/body/div[1]/div[1]/div[3]/div[1]/div[2]/form/button').click()
        time.sleep(1)
        # WebDriverWait(driver, 60, 0.1, ).until(
        #     EC.presence_of_element_located(
        #         (By.XPATH, '/html/body/div[1]/div[1]/div[3]/div')))
        return driver
    else:
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
        time.sleep(1)
        return driver
