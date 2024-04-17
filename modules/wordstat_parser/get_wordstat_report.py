import requests
import json
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(module)s.%(funcName)s - %(message)s')

logger = logging.getLogger(__name__)


class WordstatUserDataValidator:
    _regions_ids = None  # Кэширование ID регионов

    @classmethod
    def _load_region_ids(cls):
        if cls._regions_ids is None:
            with open('regions_and_ID.json', 'r', encoding='utf-8') as file:
                regions_and_ID = json.load(file)
                cls._regions_ids = set(regions_and_ID.values())  # Использование множества для ускорения проверки наличия элемента

    @staticmethod
    def _region_code_validator(geo_ids: list):
        WordstatUserDataValidator._load_region_ids()  # Загрузка и кэширование ID регионов
        for geo_id in geo_ids:
            if geo_id not in WordstatUserDataValidator._regions_ids:
                raise ValueError(f'Указан неверный код региона: {geo_id}')
        return True

    @staticmethod
    def _phrase_validator(phrases: list):
        if not all(isinstance(phrase, str) for phrase in phrases):
            raise ValueError(f'Все фразы должны быть строками. '
                             f'Некорректные фразы: {[phrase for phrase in phrases if not isinstance(phrase, str)]}')
        return True

    @staticmethod
    def validate_user_entry_data(phrases: list, geo_ids: list) -> bool:
        try:
            return (WordstatUserDataValidator._phrase_validator(phrases) and
                    WordstatUserDataValidator._region_code_validator(geo_ids))
        except ValueError as e:
            logger.exception(f'Ошибка в данных: {e}')
            raise
class WordstatParser:
    BASE_URL = 'https://api.direct.yandex.ru/live/v4/json/'

    def __init__(self, login: str, token: str):
        self.login = login
        self.token = token


    def _send_request(self, body: dict):
        try:
            logger.info(f'Тело запроса: {body}')
            response = requests.post(self.BASE_URL, json=body)
            response_data = response.json()
            logger.info(f'Ответ сервера: {response_data}')

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

    def get_report_list(self) -> list:
        body = {
                'method': 'GetWordstatReportList',
                'token': self.token
            }
        response = self._send_request(body)
        report_list = response.json()['data']
        logger.info(f'Список запросов: {report_list}')
        return report_list


    def create_wordstat_report(self, phrases: list, geo_ids: list) -> int:
        body = {
                    'method': 'CreateNewWordstatReport',
                    'param': {
                             'Phrases': phrases,
                             'GeoID': geo_ids
                                },
                    'token': self.token
                }
        response = self._send_request(body)
        report_id = response.json()['data']
        return report_id

    def delete_wordstat_report(self, report_id: int) -> bool:
        body = {
            "method": "DeleteWordstatReport",
            "param": report_id,
            'token': self.token
        }
        response = self._send_request(body)
        report_id = response.json()['data']
        logger.info(f'Удалил отчет с ID: {report_id}')
        return True






if __name__ == '__main__':
    from dotenv import load_dotenv
    import os

    load_dotenv()  # Загружает переменные окружения из .env файла
    login = os.getenv('account_login')
    token = os.getenv('account_token')

    phrases = ['купить слона', 'sadsa']
    geo_ids = [123]

    WordstatUserDataValidator.validate_user_entry_data(phrases, geo_ids)

    # parser = WordstatParser(login, token)
    # reports_list = parser.get_report_list()
    # report_id = parser.create_wordstat_report(phrases, [123])
    #delete_status = parser.delete_wordstat_report(report_id)



