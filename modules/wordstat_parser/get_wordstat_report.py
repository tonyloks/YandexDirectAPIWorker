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
        """ Загружает ID регионов из файла и кэширует их в классе. """
        if cls._regions_ids is None:
            with open('regions_and_ID.json', 'r', encoding='utf-8') as file:
                regions_and_ID = json.load(file)
                cls._regions_ids = set(regions_and_ID.values())

    @staticmethod
    def _region_code_validator(geo_ids: list):
        """ Проверяет, что каждый ID региона в списке действительно существует. """
        WordstatUserDataValidator._load_region_ids()
        for geo_id in geo_ids:
            if geo_id not in WordstatUserDataValidator._regions_ids:
                raise ValueError(f'Указан неверный код региона: {geo_id}')
        return True

    @staticmethod
    def _phrase_validator(phrases: list):
        """ Проверяет, что каждая фраза в списке является строкой. """
        if not all(isinstance(phrase, str) for phrase in phrases):
            raise ValueError(f'Все фразы должны быть строками. '
                             f'Некорректные фразы: {[phrase for phrase in phrases if not isinstance(phrase, str)]}')
        return True

    @staticmethod
    def validate_user_entry_data(phrases: list, geo_ids: list) -> bool:
        """ Проверяет валидность фраз и ID регионов, переданных пользователем. """
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
            json_body = json.dumps(body, ensure_ascii=False).encode('UTF-8')
            response = requests.post(self.BASE_URL, json_body)

            response_data = response.json()
            logger.info(f'Ответ сервера: {response_data}')

            # Проверка на наличие ошибки в ответе
            if 'error_str' in response_data:
                error = response_data['error_str']
                raise requests.exceptions.HTTPError(f"Ошибка в ответе сервера: {error}")
            else:
                return response
        except Exception as e:
            raise

    def get_report_list(self) -> list:
        """
        Возвращает список всех созданных отчетов.

        Метод в справке API: https://yandex.ru/dev/direct/doc/dg-v4/reference/GetWordstatReportList.html
        """
        body = {
                'method': 'GetWordstatReportList',
                'token': self.token
            }
        response = self._send_request(body)
        report_list = response.json()['data']
        logger.info(f'Список запросов: {report_list}')
        return report_list


    def create_wordstat_report(self, phrases: list, geo_ids: list) -> int:
        """
        Создает новый отчет.

        Метод в справке API: https://yandex.ru/dev/direct/doc/dg-v4/reference/CreateNewWordstatReport.html
        """
        body = {
                    'method': 'CreateNewWordstatReport',
                    'token': self.token,
                    'param':
                        {
                             'Phrases': phrases,
                             'GeoID': geo_ids
                        },
                }
        response = self._send_request(body)
        report_id = response.json()['data']
        logger.info(f'Создал отчет с ID: {report_id}')
        return report_id

    def get_report_status(self, report_id: int) -> str:
        """
        Получает статус отчета по ID.
        """
        report_list = self.get_report_list()
        for report in report_list:
            if report_id == report['ReportID']:
                logger.info(f'Статус отчета {report_id}: {report['StatusReport']}')
                return report['StatusReport']

    def delete_wordstat_report(self, report_id: int):
        """
        Удаляет отчет по ID.

        Метод в справке API: https://yandex.ru/dev/direct/doc/dg-v4/reference/DeleteWordstatReport.html"""
        body = {
            "method": "DeleteWordstatReport",
            "param": report_id,
            'token': self.token
        }
        self._send_request(body)
        logger.info(f'Удалил отчет с ID: {report_id}')

    def get_wordstat_report(self, report_id: int) -> list:
        """
        Получает данные по готовому отчету и возвращает вида:.
        [{'Shows': 5, 'Phrase': 'фраза 1'}, {'Shows': 15, 'Phrase': 'фраза 2'}]

        Метод в справке API: https://yandex.ru/dev/direct/doc/dg-v4/reference/GetWordstatReport.html
        """
        body = {
                    'method': 'GetWordstatReport',
                    'token': self.token,
                    'param': report_id
                    }

        response = self._send_request(body)
        data = response.json()['data'][0]['SearchedWith']
        logger.info(f'Получил данные: {data}')
        return data



if __name__ == '__main__':
    from dotenv import load_dotenv
    import os

    load_dotenv()  # Загружает переменные окружения из .env файла
    login = os.getenv('account_login')
    token = os.getenv('account_token')

    phrases = ['купить слона', 'sadsa']
    geo_ids = [123]

    WordstatUserDataValidator.validate_user_entry_data(phrases, geo_ids)

    parser = WordstatParser(login, token)
    reports_list = parser.get_report_list()
    report_id = parser.create_wordstat_report(phrases, geo_ids)


    while True:
        report_status = parser.get_report_status(report_id)
        from time import sleep
        if report_status == 'Done':
            data = parser.get_wordstat_report(report_id)
            parser.delete_wordstat_report(report_id)
            break
        else:
            sleep(5)





