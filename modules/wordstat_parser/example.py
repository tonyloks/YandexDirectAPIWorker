from get_wordstat_report import WordstatParser, WordstatUserDataValidator

if __name__ == '__main__':
    #код для получения переменных из виртуального окружения
    #удалите если не используете venv
    from dotenv import load_dotenv
    import os
    load_dotenv()

    #подставьте в кавычках '' ваш логин и токен
    login = os.getenv('account_login')
    token = os.getenv('account_token')

    #фразы и гео нужно подавать в виде списка строк и чисел соотвественно
    #айди гео содержатся в файле regions_and_ID.json
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
            data = parser.get_wordstat_report(report_id) #данные парсинга содержатся в этой переменной
            parser.delete_wordstat_report(report_id)
            break
        else:
            sleep(5)