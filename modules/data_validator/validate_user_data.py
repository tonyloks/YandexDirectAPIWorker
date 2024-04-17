import requests
import datetime
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(module)s.%(funcName)s - %(message)s')

logger = logging.getLogger(__name__)


class APIv5Validator:
    @staticmethod
    def validate(login: str, token: str):
        try:
            url = 'https://api.direct.yandex.com/json/v5/changes'

            headers = {
                'Accept-Language': 'ru',
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}',
                'Client-Login': login
            }

            body = {
                "method": "checkCampaigns",
                "params": {
                    "Timestamp": datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
                }
            }
            response = requests.post(url, headers=headers, json=body)
            if response.status_code == 200:
                if 'error' in response.json():
                    raise ValueError(response.json()['error']['error_detail'])
                else:
                    return True
            else:
                raise requests.exceptions.HTTPError('Ошибка в запросе.')
        except Exception as e:
            raise


if __name__ == '__main__':
    from dotenv import load_dotenv
    import os

    load_dotenv()  # Загружает переменные окружения из .env файла
    login = os.getenv('account_login')
    token = os.getenv('account_token')

    account_info_getter = APIv5Validator.validate(login, token)

