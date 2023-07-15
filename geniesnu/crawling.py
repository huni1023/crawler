import os
import sys
import time
import platform
import math
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from datetime import date
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

# set utils
util_path = os.pardir
if util_path not in sys.path:
    sys.path.append(os.pardir)


from utils.crawler import Cralwer
from utils.telegram_bot import TelegramBot 
from utils.helper import load_config

Project_PATH = Path(__file__).parent.absolute().parent.absolute()
Save_PATH = os.path.join(Project_PATH, 'geniuesnu', 'result')

# load .env
load_dotenv()


# load config file : 수정되어야 함
CONFIG_PATH = "config.yaml"
config = load_config(os.path.join(Project_PATH, 'utils', CONFIG_PATH))
selen_path_dict = config['selen_path']
chrome_opt_dict = config['chrome_option']

# chrome option
chrome_opt = webdriver.ChromeOptions()
for _ in chrome_opt_dict['default']:
    chrome_opt.add_argument(_)
# chrome_opt.add_experimental_option("detach", True) # prevent automatically closed tab
# chrome_opt.add_experimental_option("excludeSwitches", ["enable-logging"])

if platform.system() == 'Linux':
    for _ in chrome_opt_dict['headless']:
        chrome_opt.add_argument(_)
    chrome_opt.add_argument(f'user-agent={chrome_opt_dict["user_agent"]}')


class snugenie_crawler(Cralwer):
    global config
    def __init__(self, url):
        if platform.system() == 'Linux':
            super().__init__(selenium_path=config['selen_path']['ubuntu2'],
                            chrome_option=chrome_opt)
        else:
            raise NotImplementedError
        self.url = url
        
        
    def login(self, ID, PW):
        r"""
        Parameters
        ----------
        ID: str
        PW: str
        
        """ 
        self.driver.get(self.url)

        time.sleep(2) # TBD

        ID_ele= self.driver.find_element(By.XPATH, '//*[@id="login_id"]')
        ID_ele.send_keys(ID)

        PW_ele = self.driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div/div[1]/fieldset/ul/li[2]/span/input')
        PW_ele.send_keys(PW)

        PW_ele.send_keys(Keys.ENTER)

        assert self.driver.current_url == 'https://snugenie.snu.ac.kr/main.do'
        print('>> login done')
    

    #!# 주관 학과, 개설 학년, 학점 구조, 교과목 영역 크롤링 필요
    def search_word(self, word):
        r"""
        Parameters
        ----------
        word: str
        """
        rs = pd.DataFrame(columns='title href'.split())

        search_bar_ele = self.driver.find_element(By.XPATH, '//*[@id="optSearchWord"]')
        search_bar_ele.send_keys(word)
        search_bar_ele.send_keys(Keys.ENTER)

        time.sleep(2)

        # 과목 수
        subject_cnt_ele = self.driver.find_element(By.XPATH, '/html/body/div/div/div/div/section[3]')
        subject_cnt = int(subject_cnt_ele.find_element(By.TAG_NAME, 'strong').text)
        print('과목수: ', subject_cnt)

        subject_per_page = 20
        page_count = math.ceil(subject_cnt/subject_per_page)
        title_ls = []
        href_ls = []
        
        for page_idx in tqdm(range(page_count), '>> crawling start'):
            if page_idx < 3:
                # 과목 크롤링
                result_box = self.driver.find_element(By.XPATH, '/html/body/div/div/div/div/section[4]/div[1]')
                result_ls = result_box.find_elements(By.TAG_NAME, 'div')
                
                for one_sbj in result_ls:
                    sbj_title = one_sbj.find_element(By.CLASS_NAME, 'title').text
                    title_ls.append(sbj_title)

                    for idx, a_tag in enumerate(one_sbj.find_elements(By.TAG_NAME, 'a')):
                        if idx == 0 :
                            href_ls.append(a_tag.get_attribute('href'))
                
                # click next page
                if page_idx < page_count:
                    next_page = self.driver.find_element(By.XPATH, '/html/body/div/div/div/div/section[4]/div[2]/span[3]/a[1]')
                    print(next_page.get_attribute('href'))
                    next_page.click()
            else:
                pass
        
        rs['title'] = title_ls
        rs['href'] = href_ls

        print('>> search done: ', rs.shape)

        return rs
        

def main():
    crawler = snugenie_crawler(url='https://snugenie.snu.ac.kr')
    crawler.login(ID= os.environ.get('mysnu-id'),
          PW= os.environ.get('mysnu-pw'))
    rs = crawler.search_word('개론')
    crawler.driver.close()

     
    today = date.today().isoformat()
    rs.to_excel(f'./result/{today}_result.xlsx', index=False)

        

if __name__ == '__main__':
    main()
    