import requests
import json
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(module)s.%(funcName)s - %(message)s')

logger = logging.getLogger(__name__)

class WordstatParser:
    BASE_URL = 'https://api.direct.yandex.ru/live/v4/json/'

    def __init__(self, login: str, token: str):
        self.login = login
        self.token = token


    def _send_request(self, body: dict):
        try:
            response = requests.post(self.BASE_URL, json=body)
            response_data = response.json()
            logger.info(f'Тело запроса: {response_data}')

            # Проверка на наличие ошибки в ответе
            if 'error_str' in response_data:
                error = response_data['error_str']
                raise requests.exceptions.HTTPError(f"Ошибка в ответе сервера: {error}")
            else:
                logger.info("Ответ сервера получен.")
                return response

        except json.decoder.JSONDecodeError:
            logger.exception('Ошибка при декодировании JSON:')
            raise
        except requests.exceptions.JSONDecodeError:
            logger.exception('Ошибка при декодировании JSON:')
            raise
        except requests.exceptions.HTTPError:
            logger.exception('Ошибка при обращении к серверу.')
            raise
        except Exception as e:
            logger.exception('Неизвестная ошибка:')
            raise

    def create_new_wordstat_report(
                                self,
                                phrases: list,
                                geo_ids: list):
        body = {
                    'method': 'CreateNewWordstatReport',
                    'param': {
                             'Phrases': phrases,
                             'GeoID': geo_ids
                                },
                    'token': self.token
                }
        response = requests.post(self.BASE_URL, json=body)
        print(response)
        print(response.text)
        print(response.json())





if __name__ == '__main__':
    from dotenv import load_dotenv
    import os

    load_dotenv()  # Загружает переменные окружения из .env файла
    login = os.getenv('account_login')
    token = os.getenv('account_token')

    phrases = ['купить слона',123]
    geo_ids = [213]

    parser = WordstatParser(login, token)

