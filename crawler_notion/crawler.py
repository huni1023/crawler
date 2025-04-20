from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium import webdriver
import os
import copy
import time
import datetime
import pickle
import warnings
from sys import platform
from tqdm import tqdm
warnings.filterwarnings('ignore')

chrome_opt = webdriver.ChromeOptions()

class Crawler:
    def __init__(self, selen_path, chromeOption, main_page_link):
        """
        1. selen_path: path of chrome webdriver
        2. chromeOption: set of option arguments 
        3. main_page_link: main study crawler link
        """
        print('Current OS : ', platform)
        self.driver = webdriver.Chrome(
            executable_path=selen_path, chrome_options=chromeOption)
        self.ACC = ActionChains(self.driver)
        self.main_page_link = main_page_link
        self.BASE_DIR = os.getcwd()


    def D1(self,
            table_css, # table css selector path
            # block_css, # first block css selector path
            test_opt=False,  # 테스트 할 때
        ):
        
        self.driver.get(self.main_page_link)
        time.sleep(3)
        Table = self.driver.find_element(By.CSS_SELECTOR, table_css)
        outputLS = []

        # crawler
        # 한줄 한줄 마우스 올려서 href 확인하기
        # 날짜, 제목, 링크, 발제자
        for idx in tqdm(range(1, 50), desc='>> crawling each page meta info..'):
            temp = {}

            try:
                each_block = Table.find_element(By.CSS_SELECTOR,
                    f'#notion-app > div > div.notion-cursor-listener > div:nth-child(1) > div.notion-frame > div > div:nth-child(5) > div > div > div.notion-selectable.notion-collection_view_page-block > div:nth-child(3) > div:nth-child({idx+1})')
            except NoSuchElementException:
                print('crawling finished in: ', idx)
                break

            title_block = each_block.find_element(By.CSS_SELECTOR,
                'div:nth-child(5) > div:nth-child(1)')
            title = title_block.text
            temp['title'] = title
            day = each_block.find_element(By.CSS_SELECTOR, 'div:nth-child(1)').text
            temp['day'] = day
            people = each_block.find_element(By.CSS_SELECTOR, 
                'div:nth-child(6)').text
            temp['people'] = people

            self.ACC.move_to_element(title_block).perform()
            # if 'darwin' in platform: 
                # (80, -30/-29)하면 열리는 것: 3줄짜리
                # (80. -28)하면 열리는 것
                # 1번 idx에서 성공함 # ACC.move_by_offset(80, -30).perform() # positive direction: right, bottom
                # ACC.move_by_offset(80, -29) 
                # delay = 5
                # overlay = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CLASS_NAME, 'notion-peek-renderer')))
                # open_as_page = overlay.find_element(By.CSS_SELECTOR, 'a') 
                # link = open_as_page.get_attribute('href')
                # except StaleElementReferenceException:
                #     ACC.move_by_offset(80, -25)

            # else: print('setting')
            time.sleep(1)
            Table_re = self.driver.find_element(By.CSS_SELECTOR, table_css)
            a_blocks = Table_re.find_elements(By.CSS_SELECTOR, 'a')
            for block in a_blocks:
                link = block.get_attribute('href')
                if 'youtube' in link: continue
                elif 'dndrl' in link:
                    temp['link'] = link
                    break
            
            outputLS.append(temp)
        
        print('>> crawled dataframe: ', outputLS[:3])
        return outputLS


    def D2(self, RS1,  # D1 결과
        save_folder, # 파일 저장 위치
        title, # 파일 제목
        test_opt = False, # 테스트 할 때
        ):
        
        outputLS = copy.deepcopy(RS1)
        
        # 페이지 진입
        for idx, page in tqdm(enumerate(RS1), desc = '>> crawling each page'):
            assert type(page) == dict, print(page)
            try:
                self.driver.get(page['link']) ; time.sleep(3)
            except KeyError:
                print(f'>>> passing : ', idx)
                continue
            #!# 텍스트 모두 드러나게 클릭하는 작업

            Content = self.driver.find_element(By.CLASS_NAME, 'notion-page-content').text
            outputLS[idx]['content'] = Content
        
        if test_opt == True:
            print('>>>> Sample', outputLS[0])


        today = str(datetime.datetime.now()).replace('-', '')[2:8]
        file_name = today+ title + '.pkl'
        # file_name = today+ + '.pkl'
        save_dir = os.path.join(self.BASE_DIR, save_folder, file_name)
        with open(save_dir, 'wb') as outp:
            pickle.dump(outputLS, outp)

        self.driver.close()
        pass


if __name__ == '__main__':
    if 'darwin' in platform:
        selen_path = '/Users/huni/Dropbox/내 Mac (MacBook-Pro.local)/Downloads/chromedriver'
        chrome_opt.add_argument('start-maximized')

    elif 'win32' in platform:
        # to unable image
        chrome_opt.add_experimental_option("excludeSwitches", ["enable-logging"])
        prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_opt.add_experimental_option("prefs", prefs)
        chrome_opt.add_argument('--start-maximized')

        selen_path = r'C:\Users\jhun1\Dropbox\My PC (LAPTOP-VLNR6K8R)\Downloads\chromedriver_win32\chromedriver'


    crawler = Crawler(selen_path=selen_path, chromeOption=chrome_opt, main_page_link='https://dndrl.notion.site/28b270dfd58d497cbd031f457f02ed92?v=c081bcadc88a486683c7e7325ea99174')

    crawled_list = crawler.D1(table_css='#notion-app > div > div.notion-cursor-listener > div:nth-child(1) > div.notion-frame > div > div:nth-child(5) > div > div > div.notion-selectable.notion-collection_view_page-block',
                test_opt= False
            )

    rs2 = crawler.D2(RS1 = crawled_list, 
            save_folder = 'RESULT',
            title = '_2021 STELA 발제내용',
            test_opt= False,
            )
