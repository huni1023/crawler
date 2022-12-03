import os, re, sys, warnings, time, random, requests, zipfile
from pathlib import Path
import pandas as pd
from sys import platform
from tqdm import tqdm
warnings.filterwarnings('ignore')

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, UnexpectedAlertPresentException

parent_dir = Path(os.getcwd()).resolve().parents[0]
notion_dir = parent_dir / 'notion'
if notion_dir in sys.path:
    pass
else:
    sys.path.append(os.path.dirname(notion_dir))


from notion.crawler import Load


class Crawler(Load):
    def __init__(self, USER, image, book_angela):
        '''
        1. USER, image: args from Load
        2. book_file_name: file path of book excel containing book url
        '''

        super().__init__(USER, image)

        self.book = pd.read_excel(Path(os.getcwd()) / 'data' / book_angela)
        self.sleep_cnt = 0
        self.error_bookNumber = []

    def One_Book_Crawler(self, url):
        '''take one url and get '''
        self.driver.get(url)
        img_xPath = '/html/body/div/div[4]/div[2]/div/div/div/div/div[1]/div[1]/div[1]/div[1]/div[1]/ul/li/div/div/img[1]'
        img_f_path = self.driver.find_element(By.XPATH, img_xPath).get_attribute('src')

        response = requests.get(img_f_path) ; self.sleep_cnt += 1
        std = img_f_path.rfind('/')

        if img_f_path[-6:-4] == '_l':
            image_name_dirty = img_f_path[std+1:]
            image_name = re.sub('_l', '', image_name_dirty)
        else: 
            image_name = img_f_path[std+1:]
        
        FUll_pth = os.path.join(os.getcwd(), 'data', 'image', image_name)
        print('path: ', FUll_pth)
        
        with open(FUll_pth, 'wb') as file:
            file.write(response.content)
            file.close()
            
        self.sleep_cnt += 1
        return None
    

    def looper(self, url_ls):
        for book_number in tqdm(url_ls, desc='>>> Crawlering'):
            url = 'https://www.wendybook.com/book/detail/' + str(book_number)
            try:
                Crawler.One_Book_Crawler(self= self, url=url)
                if self.sleep_cnt % 600 == 599: time.sleep(random.randint(200, 400))
            except UnexpectedAlertPresentException:
                self.error_bookNumber.append(book_number)
        
        print('crawling done : error count is ', len(self.error_bookNumber))
        return self.error_bookNumber

    def unit_text_crawler(self):
        '''
        test crawler in various situation
        '''
        print('\n\n>>>> Crawling random 100 book')

        random_idx = random.sample(range(0, self.book.shape[0]), 100)
        sample_df = self.book.iloc[random_idx, :]
        error_book_ls = Crawler.looper(self=self, url_ls= sample_df['도서번호'].values)
        
        self.driver.quit()
        return error_book_ls

    def full_carwler(self):
        print('\n\n>>>> Crawling full book')
        error_book_ls = Crawler.looper(self=self, url_ls=self.book['도서번호'].values) 
        
        self.driver.quit()
        return error_book_ls


if __name__ == '__main__':
    crawler = Crawler(USER='huni1023', image=True, book_angela='(DB)221110_short.xlsx')
    # crawler.One_Book_Crawler('https://www.wendybook.com/book/detail/47367') # one crawler test
    # crawler.unit_text_crawler()
    crawler.full_carwler()

