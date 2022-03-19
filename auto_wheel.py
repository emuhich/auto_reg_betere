import logging
import time

import undetected_chromedriver.v2 as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


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
            options = uc.ChromeOptions()
            options.add_argument('--incognito')
            options.add_argument('--no-first-run --no-service-autorun --password-store=basic')
            options.add_argument('--disable-gpu')
            options.add_argument("--window-size=400,901")
            driver = uc.Chrome(options=options)
            driver.set_page_load_timeout(30)
            try:
                i = idx + 1
                phone = val.split(':')[0]
                password = val.split(':')[1]
                print(f'{i}/{count}')
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
                WebDriverWait(driver, 60, 0.1, ).until(
                    EC.presence_of_element_located(
                        (By.XPATH, '/html/body/div[1]/div[1]/div[3]/div')))
                driver.get('https://m.ligastavok.ru/promo/fortune')
                WebDriverWait(driver, 30, 0.1, ).until(
                    EC.presence_of_element_located(
                        (By.TAG_NAME, 'iframe')))
                d = driver.find_element(By.TAG_NAME, 'iframe')
                driver.switch_to.frame(d)
                bonus = driver.find_element(By.XPATH, '/html/body/div[1]/div[1]/div[2]/div[1]/button')
                driver.execute_script("arguments[0].click();", bonus)
                time.sleep(10)
            except:
                error += 1
                with open('works/error_wheels.txt', 'a', encoding="UTF8") as f:
                    f.write(f"{val.split(':')[0]}:{val.split(':')[1]}")
            finally:
                try:
                    driver.close()
                    driver.quit()
                    driver.dispose()
                except:
                    pass
        logging.info('Прокрутка завершена')
        logging.info(f"Сделано {count - error}/{count}")
