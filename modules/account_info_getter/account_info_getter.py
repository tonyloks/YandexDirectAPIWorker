import requests
import logging
import json

# Настройка логирования
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(module)s.%(funcName)s - %(message)s')

logger = logging.getLogger(__name__)


class AccountInfoGetter_APIv4:
    BASE_URL = 'https://api.direct.yandex.ru/live/v4/json/'

    def _send_request(self, body: dict):
        try:
            logger.info(f'Тело запроса: {body}')

            json_body = json.dumps(body, ensure_ascii=False).encode('UTF-8')
            response = requests.post(self.BASE_URL, json_body)

            response_data = response.json()
            logger.info(f'Ответ сервера: {response_data}')

            # Проверка на наличие ошибки в ответе
            if 'error_str' in response_data:
                error = response_data['error_str']
                raise requests.exceptions.HTTPError(f"Ошибка в ответе сервера: {error}")
            else:
                logger.info("Ответ сервера получен.")
                return response

        except Exception as e:
            raise


    def get_api_balls(self, login: str, token: str):

        logger.info('Получаю оставшиеся API баллы.')
        body = {
            'method': 'GetClientsUnits',
            'token': token,
            'locale': 'ru',
            'param': [login]
        }
        response = self._send_request(body)
        api_balls = response.json()['data'][0]['UnitsRest']
        logger.info(f'Апи баллов на аккаунте: {api_balls}')
        return api_balls #забираю количество балов для аккаунта

    def get_balance(self, login: str, token: str):
        logger.info('Получаю баланс аккаунта')
        body = {
            'method': 'AccountManagement',
            'token': token,
            'locale': 'ru',
            'param': {
                'Action': 'Get',
                "SelectionCriteria": {
                        'Logins': [login]
                            }
                    }
                }
        response = self._send_request(body)
        balance = response.json()['data']['Accounts'][0]['Amount']
        balance = float(balance) if balance else None
        logger.info(f'Оставшийся баланс аккаунта: {balance}')
        return balance



if __name__ == '__main__':
    from dotenv import load_dotenv
    import os

    load_dotenv()  # Загружает переменные окружения из .env файла
    login = os.getenv('account_login')
    token = os.getenv('account_token')

    account_info_getter = AccountInfoGetter_APIv4()

    balls = account_info_getter.get_api_balls(login, token)

    balance = account_info_getter.get_balance(login, token)

