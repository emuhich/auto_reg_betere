import json
import logging
import random
import re
import configparser
from fake_useragent import UserAgent

import requests

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
