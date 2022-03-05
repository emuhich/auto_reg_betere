import time

import undetected_chromedriver.v2 as uc
from selenium.webdriver.common.by import By


def get_count_total():
    with open('total.txt', 'r', encoding='utf-8') as file:
        for idx, val in enumerate(file):
            i = idx + 1
        return i


def wheel():
    """Прокрутка колеса."""
    count = get_count_total()
    with open('total.txt', 'r', encoding='utf-8') as file:
        for idx, val in enumerate(file):
            try:
                options = uc.ChromeOptions()
                options.add_argument('--incognito')
                options.add_argument('--no-first-run --no-service-autorun --password-store=basic')
                options.add_argument('--disable-gpu')
                driver = uc.Chrome(options=options)
                driver.set_page_load_timeout(30)
                i = idx + 1
                phone = val.split(':')[0]
                password = val.split(':')[1]
                print(f'{i}/{count}')
                driver.get('https://www.ligastavok.ru/')
                driver.maximize_window()
                time.sleep(1)
                driver.find_element(By.XPATH,
                                    '/html/body/div/header/div/div[3]/button/span/span').click()
                time.sleep(1)
                password_input = driver.find_element(By.XPATH,
                                                     '/html/body/div[1]/div[5]/div[2]/div[3]/div[1]/div[2]/form/div[2]/input')
                time.sleep(1)
                password_input.send_keys(password)
                time.sleep(2)
                phone_input = driver.find_element(By.CSS_SELECTOR,
                                                  '#auth > div:nth-child(1) > input')
                time.sleep(1)
                phone_input.click()
                phone_input.send_keys(phone)
                time.sleep(2)
                driver.find_element(By.CSS_SELECTOR,
                                    '#auth > button').click()
                time.sleep(8)
                driver.get('https://www.ligastavok.ru/promo/fortune')
                time.sleep(5)
                d = driver.find_element(By.TAG_NAME, 'iframe')
                driver.switch_to.frame(d)
                bonus = driver.find_element(By.XPATH, '/html/body/div[1]/div[1]/div[2]/div[1]/button')
                driver.execute_script("arguments[0].click();", bonus)
                time.sleep(10)
                driver.close()
            except:
                with open('error_wheels.txt', 'a', encoding="UTF8") as f:
                    f.write(f"{val.split(':')[0]}:{val.split(':')[1]}\n")
