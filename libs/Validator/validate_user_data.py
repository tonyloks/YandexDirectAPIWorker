import requests
import datetime

class APIv5Validator:
    @staticmethod
    def validate(login: str, token: str):
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
            raise ValueError('Ошибка в запросе.')

