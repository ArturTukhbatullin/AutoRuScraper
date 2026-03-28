from scraper.AutoRuScraper import AutoRuScraper

import random
import os

PARSE_URL = 'https://auto.ru/'
PATH_WEB_DRIVER = 'scraper/WebDrivers/chromedriver-win64/chromedriver.exe'

cars_dict = {
            # 'volkswagen':['golf_r']
            # 'volkswagen':['golf','polo','golf_r'],
             'lixiang':['L6','L7','L9'],
            #  'vaz':['granta'],
            #  'mercedes':['e_klasse','c_klasse']
             }

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

                if MODEL in ['golf_r','L9','L7','L6']:
                    GET_DETAILS = True
                else: 
                    GET_DETAILS = False

                scraper = AutoRuScraper(PARSE_URL = PARSE_URL,
                                PATH_WEB_DRIVER = PATH_WEB_DRIVER,
                                params = params,
                                GET_DETAILS = GET_DETAILS)
            
                scraper.main(pause_sec=random.randint(3,5),
                        max_page_num = None)
            else:
                print(MARK, MODEL, 'skipped')

            
