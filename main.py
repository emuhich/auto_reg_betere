import logging
import re
import warnings
from multiprocessing import freeze_support
import requests as requests

from auto_wheel import wheel, get_count_total
from dolphin import multiple_create_browser
from exeptions import AccountError, NoString, NoMoney, AccountErrorBettery, NoNumber
from league_spacer import start_spacer
from vac_sms_api import check_balance, get_phone, bad_number
import registration

warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')
error_inn = 0

def suggest_inn(surname, name, patronymic, birthdate, doctype, docnumber):
    """Получаем инн."""
    docnumber = f'{docnumber[:2]} {docnumber[2:4]} {docnumber[4:10]}'
    url = "https://service.nalog.ru/inn-proc.do"
    data = {
        "fam": surname,
        "nam": name,
        "otch": patronymic,
        "bdate": birthdate,
        "bplace": "",
        "doctype": doctype,
        "docno": docnumber,
        "c": "innMy",
        "captcha": "",
        "captchaToken": "",
    }
    try:
        resp = requests.post(url=url, data=data)
        resp.raise_for_status()
        inn = resp.json()
        inn = inn['inn']
    except Exception:
        logging.debug(f"Ошибка при выдачи инн {name} {surname}")
        inn = False
        return inn
    return inn


def log():
    file_log = logging.FileHandler('bot_log.log', encoding='utf8')
    console_out = logging.StreamHandler()
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s, %(levelname)s, %(message)s',
        handlers=(file_log, console_out),
    )

    logging.getLogger('undetected_chromedriver').setLevel('CRITICAL')
    logging.getLogger('selenium').setLevel('CRITICAL')
    logging.getLogger('asyncio').setLevel('CRITICAL')
    logging.getLogger('uc').setLevel('CRITICAL')
    logging.getLogger('concurrent').setLevel('CRITICAL')
    logging.getLogger('requests').setLevel('CRITICAL')
    logging.getLogger('socks').setLevel('CRITICAL')
    logging.getLogger('charset_normalizer').setLevel('CRITICAL')
    logging.getLogger('urllib3').setLevel('CRITICAL')
    logging.getLogger('dotenv').setLevel('CRITICAL')


def get_phone_pref(tel, idNum):
    prefics = tel[1:4]
    pref = '986'
    while prefics == pref:
        bad_number(idNum)
        phone = get_phone()
        tel = phone['tel']
        idNum = phone['idNum']
        prefics = tel[1:4]
    return tel, idNum


def parse_txt_acc(count, pref=False):
    """Достаем данные из текстовика."""
    global error_inn
    logging.debug(f'Резервируем номера количество: {count}')
    acc_list = []
    indx = 0
    if not check_balance(count):
        raise NoMoney("Не хватает дененг на Vac-Sms")
    for i in range(0, count):
        indx += 1
        try:
            with open('works/result.txt', encoding='utf-8') as f:
                lines = f.readlines()
            str = lines[0]
            pattern = re.compile(re.escape(str))
            with open('works/result.txt', 'w', encoding='utf-8') as f:
                for line in lines:
                    result = pattern.search(line)
                    if result is None:
                        f.write(line)
        except Exception:
            raise NoString("Кончились строки")
        parts = str.split(' ', )
        ps = str.split(',')[3]

        name = parts[1]
        surnames = parts[0]
        patronymic = parts[2].replace(',', '')
        date_of_birth = parts[5].replace(',', '')
        passport = ps.replace(' ', '')
        inn = suggest_inn(surnames, name, patronymic, date_of_birth, '21', passport)
        if inn is not False:
            phone = get_phone()
            tel = phone['tel']
            idNum = phone['idNum']
            if pref is True:
                tel, idNum = get_phone_pref(tel, idNum)
            acc = {'date_of_birth': date_of_birth,
                   'passport': passport,
                   'patronymic': patronymic,
                   'name': name,
                   'surnames': surnames,
                   'inn': inn,
                   'tel': tel,
                   'idNum': idNum,
                   'number_process': indx,
                   }
            acc_list.append(acc)
        else:
            error_inn += 1

    return acc_list


def generate_list(count):
    data = []
    a = count // 2
    for i in range(0, a):
        data.append('2')
    b = count % 2
    if b > 0:
        data.append('1')
    return data


def get_count_result():
    with open('works/result.txt', 'r', encoding='utf-8') as file:
        for idx, val in enumerate(file):
            i = idx + 1
        return i


def main():
    global error_inn
    log()

    menu = input(f"Выберите пункт.\n"
                 f"1.Создать аккаунты.\n"
                 f"2.Прокрутить колесо\n"
                 f"3.Проставка\n"
                 f"4.Создать профиля Dolphin\n")
    if menu == '1':
        try:
            string_count = get_count_result()
        except UnboundLocalError:
            logging.error('Пустой файл result.txt')
        else:
            while True:
                count = input(f"Введите количество аккаунтов которое хотите сделать. Не больше {string_count}.\n")
                if int(count) > string_count:
                    print(f"Вы не можете сделать аккаунтов больше чем строк!!!. Максимально: {string_count}")
                else:
                    break
            spisok = generate_list(int(count))
            acc_error = 0
            other_errors = 0
            logging.debug("Бот начал регестрировать аккаунты")
            for i in spisok:
                try:
                    data = parse_txt_acc(int(i))
                    registration.start_registration(data)
                except NoString as error:
                    logging.error(error)
                    break
                except NoMoney as error:
                    logging.error(error)
                    break
                except AccountError as error:
                    logging.error(error)
                    acc_error += 1
                except AccountErrorBettery:
                    continue
                except NoNumber as error:
                    logging.error(error)
                    break
                except Exception as error:
                    other_errors += 1
                    logging.error(error)
            ready = get_count_total()
            logging.debug(
                f"Регистрация завершена, зарегистрировано:{ready}/{count}, ошибки инн: {error_inn},"
                f" повторки: {acc_error}, другие ошибки: {other_errors}")
    elif menu == '2':
        logging.debug('Начало прокрутки, все аккаунты беруться из файла total.txt')
        wheel()
    elif menu == '3':
        logging.debug('Начало проставки, все аккаунты беруться из файла spacer.txt')
        url = input('Введите ссылку на матч\n')
        start_spacer(url)
    elif menu == '4':
        logging.debug('Начало создания профилей Dolphin')
        count = input('Введите количество профилей\n')
        result = multiple_create_browser(int(count))
        with open('works/dolphin.txt', 'a', encoding="UTF8") as f:
            for i in result:
                f.write(f'{str(i)}\n')
        logging.debug(f'Профиля созданы в количестве {len(result)} штук')


if __name__ == '__main__':
    freeze_support()
    main()
