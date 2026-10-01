from scraper.AutoRuScraper import AutoRuScraper
from scraper.AutoRuDB import AutoRuDB
import random
import os
from dotenv import load_dotenv
load_dotenv()


PARSE_URL = 'https://auto.ru/'

CITY='kazan'
cars_dict = {
            'volkswagen':['golf_r']
            # 'volkswagen':['golf','polo','golf_r'],
            #  'lixiang':['L6','L7','L9'],
            #  'vaz':['granta'],
            #  'mercedes':['e_klasse','c_klasse']
             }


conn_params = {
    'username' : os.getenv('db_username'),
    'password' : os.getenv('db_password'),
    'host' : os.getenv('db_host'),
    'port' : os.getenv('db_port')
}
db = AutoRuDB('main', **conn_params)

def check_if_file_exist(params):

    files = os.listdir('data/csv')
    
    file = fr"{params['CITY']}_{params['MARK']}_{params['MODEL']}.csv"

    if file in files:
        return True
    else:
        return False


if __name__ == '__main__':

    for MARK in cars_dict.keys():
        
        for MODEL in cars_dict[MARK]:
        
            params = {'CITY':CITY,'MARK':MARK,'MODEL':MODEL}

            if check_if_file_exist(params)==False:

                if MODEL in ['golf_r','L9','L7','L6']:
                    GET_DETAILS = True
                else: 
                    GET_DETAILS = False

                scraper = AutoRuScraper(PARSE_URL = PARSE_URL,
                                params = params,
                                GET_DETAILS = GET_DETAILS)
            
                scraper.main(pause_sec=random.randint(3,5),
                        max_page_num = None)

                # print(scraper.results.dtypes)
                db.create_table()
                db.load_data_to_db(scraper.results)
                
            else:
                print(MARK, MODEL, 'skipped')

            
