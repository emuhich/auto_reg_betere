import logging
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from chromedriver.locate import DRIVER_DIR
from dolphin import start_dolphin_automation, login_ligue, refactoring_profile


def get_count_total():
    """Достаем колличество аккаунтов из total.txt."""
    with open('works/total.txt', 'r', encoding='utf-8') as file:
        try:
            for idx, val in enumerate(file):
                i = idx + 1
            return i
        except:
            return 0


def wheel():
    """Прокрутка колеса."""
    count = get_count_total()
    error = 0
    with open('works/total.txt', 'r', encoding='utf-8') as file:
        for idx, val in enumerate(file):
            profile_id = val.split(':')[2]
            port = start_dolphin_automation(int(profile_id))
            options = Options()
            options.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
            # Change chrome driver path accordingly
            driver = webdriver.Chrome(options=options, executable_path=f"{DRIVER_DIR}\chromedriver")
            driver.set_page_load_timeout(30)
            try:
                i = idx + 1
                phone = val.split(':')[0]
                password = val.split(':')[1]
                print(f'{i}/{count}')
                driver.set_window_size(400, 901)
                driver.get('https://m.ligastavok.ru')
                time.sleep(1)
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
                    driver.get('https://m.ligastavok.ru/promo/fortune')
                    WebDriverWait(driver, 30, 0.1, ).until(
                        EC.presence_of_element_located(
                            (By.TAG_NAME, 'iframe')))
                    d = driver.find_element(By.TAG_NAME, 'iframe')
                    driver.switch_to.frame(d)
                    bonus = driver.find_element(By.XPATH, '/html/body/div[1]/div[1]/div[2]/div[1]/button')
                    driver.execute_script("arguments[0].click();", bonus)
                    time.sleep(10)
                driver.get('https://m.ligastavok.ru/promo/fortune')
                WebDriverWait(driver, 30, 0.1, ).until(
                    EC.presence_of_element_located(
                        (By.TAG_NAME, 'iframe')))
                d = driver.find_element(By.TAG_NAME, 'iframe')
                driver.switch_to.frame(d)
                bonus = driver.find_element(By.XPATH, '/html/body/div[1]/div[1]/div[2]/div[1]/button')
                driver.execute_script("arguments[0].click();", bonus)
                time.sleep(10)
                refactoring_profile(profile_id=profile_id, wheel=True)
            except:
                refactoring_profile(profile_id=profile_id, wheel=False)
                error += 1
                with open('works/error_wheels.txt', 'a', encoding="UTF8") as f:
                    f.write(f"{val.split(':')[0]}:{val.split(':')[1]}:{val.split(':')[2]}")
            finally:
                try:
                    driver.close()
                    driver.quit()
                    driver.dispose()
                except:
                    pass
        logging.info('Прокрутка завершена')
        logging.info(f"Сделано {count - error}/{count}")
