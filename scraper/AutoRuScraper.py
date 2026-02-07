from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from tqdm import tqdm
from datetime import date

from bs4 import BeautifulSoup
import re

import time
import json
import pandas as pd

from loguru import logger
logger.add("logs/log.log", rotation="500 MB",compression='zip')


TIMEOUT = 20

class AutoRuScraper:

    def __init__(self, PARSE_URL, PATH_WEB_DRIVER,params,GET_DETAILS):

        self.CITY = params['CITY']
        self.MARK = params['MARK']
        self.MODEL = params['MODEL']
        self.PARSE_URL = PARSE_URL+ fr'{self.CITY}/cars/{self.MARK}/{self.MODEL}/all/?sort=price-asc'
        self.PATH_WEB_DRIVER = PATH_WEB_DRIVER
        self.GET_DETAILS = GET_DETAILS

    def __create_driver__(self):
        chrome_options = Options()
        # Указывать User-Agent
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36')
        # Другие полезные заголовки и настройки
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')  # Скрываем автоматизацию
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        service = Service(executable_path=self.PATH_WEB_DRIVER)
        driver = webdriver.Chrome(service=service, options=chrome_options)

        self.driver = driver
        self.service = service

    @staticmethod
    def make_pause(sec):
        time.sleep(sec)

    def save_cookies_to_json(self, filename='cookies.json'):

        """Сохранить куки в JSON (читаемый формат)"""

        cookies = self.driver.get_cookies()
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(cookies, file, ensure_ascii=False, indent=2)
        print(f"Сохранено {len(cookies)} кук в JSON")

    def get_page_list(self):
        
        bs = BeautifulSoup(self.page_source, 'html.parser',from_encoding='utf-8')
        pages = bs.find_all('span', {'class' : 'Button__text'})
        pages = [i.text for i in pages]
        try:
            last_page = int(pages[-9])
        except:
            last_page = 1
        pages = [i+1 for i in range(last_page)]
        logger.info(fr"Всего страниц : {last_page}")        
        self.pages = pages

    def parse_page_with_bs4(self):

        bs = BeautifulSoup(self.page_source, 'html.parser',from_encoding='utf-8')
        all_cars = bs.find_all('div', {'class' : 'ListingCars__items'})
        all_cars = all_cars[0].find_all('div', {'class':'ListingCars__universalSnippetWrapper'})
        
        logger.info(fr"Всего машин на странице: {len(all_cars)}")

        parsed_millege = [str(str(all_cars[i].find('div', {'class': re.compile('ListingItemUniversalCondition__status.*')}).div.text).replace('\xa0','').replace('км',' км')) for i in range(len(all_cars))]        
        parsed_title = [str(all_cars[i].find('a', {'class':'ListingItemTitle__link'}).text).replace('\xa0','').replace('км',' км').split(', ') for i in range(len(all_cars))]
        parsed_url = [all_cars[i].find('a', {'class':'ListingItemTitle__link'})['href'] for i in range(len(all_cars))]
        parsed_cost = [float(str(all_cars[i].find('div', {'class': re.compile('ListingItemUniversalPrice__title.*')}).div.text).replace('\xa0','').replace('₽','').replace('от','')) for i in range(len(all_cars))]

        parsed_items = [0]*len(all_cars)

        for i in range(len(all_cars)):
            temp = all_cars[i].find_all('div',{'class': re.compile('ListingItemUniversalSpecs__specs.*')})[0].find_all('div')
            pre_temp=[]
            for j in range(len(temp)):
                pre_temp1 = str(temp[j].text).replace('\xa0',' ')
                pre_temp.append(pre_temp1)

            parsed_items[i] = pre_temp

        return parsed_title,parsed_items,parsed_url,parsed_cost,parsed_millege

    # @staticmethod
    def prepare_output_df(self, df_orig):
        df = df_orig.copy()

        df['name'] = df['title'].apply(lambda x: x[0])

        df['engine_volume'] = df['items'].apply(lambda x: list(x)[0].split(',')[0].replace("['",''))
        df['motor_power'] = df['items'].apply(lambda x: list(x)[0].split(',')[1].replace(' ',''))
        df['fuel_type'] = df['items'].apply(lambda x: list(x)[0].split(',')[2].replace(' ',''))
        df['body_type'] = df['items'].apply(lambda x: list(x)[1])
        df['drive_type'] = df['items'].apply(lambda x: list(x)[2])
        df['gearbox_type'] = df['items'].apply(lambda x: list(x)[3])

        if self.GET_DETAILS:

            df['owners_num'] = df['owners_num'].apply(lambda x: list(x)[0])
            df['configuration'] = df['details'].apply(lambda x: list(x)[0])
            df['steering_wheel_type'] = df['details'].apply(lambda x: list(x)[1])
            df['color'] = df['details'].apply(lambda x: list(x)[2])

        df['parse_date'] = str(date.today())

        return df

    def parse_page_with_bs4_postprocess(self,parsed_title,parsed_items,parsed_url,parsed_cost,parsed_millege,
                                        parsed_owners = None,parsed_characters = None):

        df = pd.DataFrame({'title':parsed_title,
                        'items':parsed_items,
                        'owners_num':parsed_owners,
                        'details':parsed_characters,
                        'url':parsed_url,
                        'cost':parsed_cost,
                        'millege':parsed_millege                        
                        })

        df_postprocessed = self.prepare_output_df(df)

        self.results = df_postprocessed

    def parse_car_details(self,url,pause_sec):

        self.make_pause(pause_sec)
        original_tab = self.driver.current_window_handle
        self.driver.execute_script(fr"window.open('{url}');")

        # Переключиться на новую вкладку
        self.driver.switch_to.window(self.driver.window_handles[1])
        self.make_pause(pause_sec)

        html2 = self.driver.page_source
        bs2 = BeautifulSoup(html2, 'html.parser',from_encoding='utf-8')
        self.make_pause(pause_sec)

        owners = bs2.find_all('ul', {'class':'CardInfoSummary__list-jpQIS'})[0]
        owners = owners.find_all('li',{'class':'CardInfoSummarySimpleRow-CY5TE'})
        owners = [i.find('div',{'class':'CardInfoSummarySimpleRow__content-IIKcj'}).text.replace('\xa0',' ') for i in owners if i.find('div',{'class':'CardInfoSummarySimpleRow__label-uJbU8'}).text=='Владельцы']

        characters = bs2.find_all('ul',{'class':'CardInfoSummary__list-jpQIS'})[1]
        characters = characters.find_all('li',{'class':'CardInfoSummaryComplexRow-CngDv'})
        characters_1 = [i.text.replace('Комплектация','') for i in characters  if i.find('div',{'class':'CardInfoSummaryComplexRow__cellTitle-S_R1k'}).text in ['Комплектация']]
        characters_2 = [i.text.replace('Руль','')  for i in characters if i.find('div',{'class':'CardInfoSummaryComplexRow__cellTitle-S_R1k'}).text in ['Руль']]
        characters_3 = [i.text.replace('Цвет','')  for i in characters if i.find('div',{'class':'CardInfoSummaryComplexRow__cellTitle-S_R1k'}).text in ['Цвет']]
        
        def replace_empty_list(characters_1):
            if characters_1 == []:
                characters_1 = [None]
            return characters_1
        
        owners = replace_empty_list(owners)
        characters_1 = replace_empty_list(characters_1)
        characters_2 = replace_empty_list(characters_2)
        characters_3 = replace_empty_list(characters_3)

        characters_clean = characters_1 + characters_2 + characters_3

        # Возвращаемся к исходной вкладке
        self.driver.close()
        self.driver.switch_to.window(original_tab)

        return owners, characters_clean

    def save_results(self):

        self.results.to_csv(fr'data/csv/{self.CITY}_{self.MARK}_{self.MODEL}.csv',index=False,sep=';')

    def get_next_page(self, pause_sec):

        try:

            current_url = self.driver.current_url

            # Ожидание появления элемента
            try:
                WebDriverWait(self.driver, TIMEOUT).until(
                    EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "Следующая, Ctrl"))
                )
            except:
                logger.warning('TimeOut: элемента нет')
        

            # Ожидание, пока элемент станет кликабельным
            try:
                WebDriverWait(self.driver, TIMEOUT).until(
                    EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Следующая, Ctrl"))
                )
            except:
                logger.warning('TimeOut: элемент не кликабельный')
            
            # Скрол до списка страниц
            element = self.driver.find_element(By.PARTIAL_LINK_TEXT, "Следующая, Ctrl")
            self.driver.execute_script("""
                arguments[0].scrollIntoView({behavior: 'smooth',
                block: 'center',
                inline: 'center'});""",
            element)

            # Пробуем клик через JavaScript как запасной вариант
            try:
                element.click()
            except:
                # Если обычный клик не работает, пробуем через JavaScript
                self.driver.execute_script("arguments[0].click();", element)
                logger.info('Клик через driver.execute_script()')

            # Пауза для заргузки страницы
            self.make_pause(pause_sec)

            # Ожидаем, пока URL изменится (это признак перехода на новую страницу)
            try:
                WebDriverWait(self.driver, TIMEOUT).until(
                    lambda d: d.current_url != current_url
                )
            except:
                logger.warning(fr'TimeOut: URL не поменялся ({self.driver.current_url} & {current_url})')

                try:
                    WebDriverWait(self.driver, 2*TIMEOUT).until(
                    lambda d: d.current_url != current_url
                )
                except:
                    logger.warning(fr'TimeOut: URL не поменялся после второго перехода ({self.driver.current_url} & {current_url})')              
                    
                    try:
                        href = element.get_attribute("href")
                        self.driver.get(href) 
                        self.make_pause(pause_sec)

                        WebDriverWait(self.driver, TIMEOUT).until(
                        lambda d: d.current_url != current_url
                        )

                    except:
                        logger.warning(fr'TimeOut: URL не поменялся после явного перехода по ссылке ({self.driver.current_url} & {current_url})')              

            # Ожидаем загрузки DOM
            try:
                WebDriverWait(self.driver, TIMEOUT).until(
                    lambda d: d.execute_script('return document.readyState') == 'complete'
                )
            except:
                logger.warning(fr'TimeOut: DOM не загрузился')

            # обновление page_source
            self.page_source = self.driver.page_source
        
        except Exception as e:
            logger.error(f"Ошибка при переходе на следующую страницу: {e}")
            raise

    def main(self, pause_sec : int = 3, max_page_num :int = None):

        logger.info(fr"Начало парсинга {self.MARK} {self.MODEL}")
        
        # Препроцесс
        self.__create_driver__()
        self.driver.get(self.PARSE_URL)
        self.make_pause(pause_sec)
        self.page_source = self.driver.page_source

        # Работа с cookie
        self.save_cookies_to_json(filename='cookie/autoru_cookie.json')
        logger.info(fr"Куки сохранены")

        # Список всех страниц
        self.get_page_list()

        # Парсинг первой страницы
        page=1
        parsed_title,parsed_items,parsed_url,parsed_cost,parsed_millege = self.parse_page_with_bs4()
        logger.info(fr"Парсинг страницы {page} с bs4 завершен")
        page+=1

        if self.GET_DETAILS:
            parsed_owners = [0] * len(parsed_url)
            parsed_characters = [0] * len(parsed_url)
            for ind in range(len(parsed_url)):
                parsed_owners[ind], parsed_characters[ind] = self.parse_car_details(parsed_url[ind], pause_sec)
                print(parsed_characters[ind])
                print(parsed_owners[ind])
            logger.info(fr"Парсинг деталей с каждой страницы на странице {page} с bs4 завершен")
        else:
            parsed_owners, parsed_characters = None,None

        for i in range(len(parsed_items)):
            print(len(parsed_items[i]),parsed_items[i])

        # Парсинг остальных страниц
        if max_page_num == None:
            max_page_num = self.pages[-1]
            
        for i in range(page, max_page_num+1):
            self.get_next_page(pause_sec)
            self.make_pause(pause_sec)
            parsed_title_page,parsed_items_page,parsed_url_page,parsed_cost_page,parsed_millege_page = self.parse_page_with_bs4()
            logger.info(fr"Парсинг страницы {i} с bs4 завершен")

            if self.GET_DETAILS:
                parsed_owners_page = [0] * len(parsed_url_page)
                parsed_characters_page = [0] * len(parsed_url_page)
                for ind in range(len(parsed_url_page)):
                    parsed_owners_page[ind], parsed_characters_page[ind] = self.parse_car_details(parsed_url_page[ind], pause_sec)
                logger.info(fr"Парсинг деталей с каждой страницы на странице {page} с bs4 завершен")

            parsed_title+=parsed_title_page
            parsed_items+=parsed_items_page
            parsed_url+=parsed_url_page
            parsed_cost+=parsed_cost_page
            parsed_millege+=parsed_millege_page
            if self.GET_DETAILS:
                parsed_owners+=parsed_owners_page
                parsed_characters+=parsed_characters_page
            else:
                parsed_owners, parsed_characters = None,None

        self.parse_page_with_bs4_postprocess(parsed_title,parsed_items,parsed_url,parsed_cost,parsed_millege, parsed_owners,parsed_characters)
        logger.info(fr"ПострПроцесс bs4 завершен")

        self.save_results()
        logger.info(fr"Результаты сохранены в csv")
        self.driver.close()
