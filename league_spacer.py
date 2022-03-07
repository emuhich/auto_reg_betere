import undetected_chromedriver.v2 as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait


def get_count_total():
    with open('spacer.txt', 'r', encoding='utf-8') as file:
        for idx, val in enumerate(file):
            i = idx + 1
        return i


def open_ligue():
    options = uc.ChromeOptions()
    options.add_argument('--incognito')
    options.add_argument('--no-first-run --no-service-autorun --password-store=basic')
    options.add_argument('--disable-gpu')
    driver = uc.Chrome(options=options)
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    driver.get('https://www.ligastavok.ru/registration')


def start_spacer():
    open_ligue()
