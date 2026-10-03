from scraper.AutoRuScraper import AutoRuScraper
from scraper.AutoRuDB import AutoRuDB
import random
import os
from dotenv import load_dotenv
load_dotenv()

PARSE_URL = 'https://auto.ru/'

# Параметры подключения к БД
conn_params = {
    'username' : os.getenv('db_username'),
    'password' : os.getenv('db_password'),
    'host' : os.getenv('db_host'),
    'port' : os.getenv('db_port')
}
# Определяю экземпляр класса с БД
db = AutoRuDB('main', **conn_params)
autoru_init_params = db.get_init_params() # таблица с объектами для парсинга

if __name__ == '__main__':

    for row in autoru_init_params.to_numpy():
        _, CITY, MARK, MODEL, GET_DETAILS, _ = row

        params = {'CITY':CITY,'MARK':MARK,'MODEL':MODEL}

        # Определяю экземпляр класса скрапера
        scraper = AutoRuScraper(PARSE_URL = PARSE_URL,
                                params = params,
                                GET_DETAILS = GET_DETAILS)
        scraper.main(pause_sec=random.randint(3,5),
                        max_page_num = None)

        # Сохранение в БД
        db.create_table()
        db.load_data_to_db(scraper.results)

            
