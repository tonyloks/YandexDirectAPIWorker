from validate_user_data import APIv5Validator
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(module)s.%(funcName)s - %(message)s')

logger = logging.getLogger(__name__)


if __name__ == '__main__':

    #код для получения переменных из виртуального окружения
    #удалите если не используете venv
    from dotenv import load_dotenv
    import os
    load_dotenv()

    #подставьте в кавычках '' ваш логин и токен
    login = os.getenv('account_login')
    token = os.getenv('account_token')

    status = APIv5Validator.validate(login, token)
    logger.info(f'Статус валидации данных: {status}')
