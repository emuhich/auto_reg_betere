import requests

VAC_TOKEN = 'd5ff424b443e4472bd1b1a1db924811e'


def get_phone():
    """Покупка номера на VAC sms."""
    params = {
        'apiKey': VAC_TOKEN,
        'service': 'cp',
        'country': 'ru',
        'operator': 'mtt',
        'softId': 1025
    }
    phone_count = requests.get('https://vak-sms.com/api/getCountNumber/', params=params)
    value = phone_count.json()
    if int(value['cp']) < 20:
        params = {
            'apiKey': VAC_TOKEN,
            'service': 'cp',
            'country': 'ru',
            'operator': 'mtt',
            'rent': True,
            'softId': 1025
        }
    phone = requests.get('https://vak-sms.com/api/getNumber/', params=params)
    return phone.json()


def check_balance(count):
    """Проверка баланса VAC sms."""
    summ = 10
    params = {
        'apiKey': VAC_TOKEN,
        'service': 'cp',
        'country': 'ru',
        'operator': 'mtt'
    }
    phone_count = requests.get('https://vak-sms.com/api/getCountNumber/', params=params)
    value = phone_count.json()
    if int(value['cp']) < 20:
        summ = 25
    params = {
        'apiKey': VAC_TOKEN,
    }
    balance = requests.get('https://vak-sms.com/api/getBalance', params=params).json()
    if int(balance['balance']) < summ * count:
        return False
    return True


def bad_number(idNum):
    """Смена номера."""
    params = {
        'apiKey': VAC_TOKEN,
        'status': 'end',
        'idNum': idNum
    }
    status = requests.get('https://vak-sms.com/api/setStatus/?apiKey={apiKey}&status={status}&idNum={idNum}',
                          params=params).json()
    if status['status'] == 'smsReceived':
        raise Exception("Ошибка отмены номера: на данный номер уже получен код подтверждения, отмена невозможна.")
    elif status['status'] == 'waitSMS':
        raise Exception("на данные номер уже отправлено смс, отмена невозможна. Ожидайте код.")


def again_sms(idNum):
    """Повторное получение смс."""
    params = {
        'apiKey': VAC_TOKEN,
        'status': 'send',
        'idNum': idNum
    }
    status = requests.get('https://vak-sms.com/api/setStatus/?apiKey={apiKey}&status={status}&idNum={idNum}',
                          params=params).json()
    if status['status'] == 'smsReceived':
        raise Exception("Ошибка отмены номера: на данный номер уже получен код подтверждения, отмена невозможна.")
    elif status['status'] == 'waitSMS':
        raise Exception("на данные номер уже отправлено смс, отмена невозможна. Ожидайте код.")


def get_sms_code(idNum):
    """Получение sms кода."""
    params = {
        'apiKey': VAC_TOKEN,
        'idNum': idNum
    }
    code = requests.get('https://vak-sms.com/api/getSmsCode', params=params).json()
    return code
