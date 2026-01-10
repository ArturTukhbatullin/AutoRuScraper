from scraper.AutoRuScraper import AutoRuScraper

import random
import os

PARSE_URL = 'https://auto.ru/'
PATH_WEB_DRIVER = 'D:\WebDrivers\chromedriver-win64/chromedriver.exe'

cars_dict = {
            'volkswagen':['polo'],
            # 'volkswagen':['golf','polo','golf_r'],
            #  'lixiang':['L6','L7','L9'],
            #  'vaz':['2114','granta'],
            #  'mercedes':['e_klasse','c_klasse']
             }

# cars_dict = {
#             'vaz':['granta'],
#             }

CITY='kazan'


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
                scraper = AutoRuScraper(PARSE_URL = PARSE_URL,
                                PATH_WEB_DRIVER = PATH_WEB_DRIVER,
                                params = params)
            
                scraper.main(pause_sec=random.randint(3,5),
                        max_page_num = None)
            else:
                print(MARK, MODEL, 'skipped')

            
