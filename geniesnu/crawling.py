import os
import re
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
from selenium.webdriver.support import expected_conditions as EC

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
        self.wait = WebDriverWait(self.driver, 10)
        
        
    def login(self, ID, PW):
        r"""
        Parameters
        ----------
        ID: str
        PW: str
        
        """ 
        self.driver.get(self.url)
        
        self.wait.until(EC.visibility_of_all_elements_located(
                        (By.XPATH, '//*[@id="login_id"]')
                        )
                    )
        ID_ele= self.wait.until(
                    # EC.element_to_be_clickable(
                    EC.visibility_of(
                    # EC.visibility_of_all_elements_located(
                        (self.driver.find_element(By.XPATH, '//*[@id="login_id"]'))
                    )
                )
        
        ID_ele.send_keys(ID)
        

        PW_ele = self.driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div/div[1]/fieldset/ul/li[2]/span/input')
        PW_ele.send_keys(PW)

        PW_ele.send_keys(Keys.ENTER)

        time.sleep(2)
        assert self.driver.current_url == 'https://snugenie.snu.ac.kr/main.do'
        print('>> login done')
    

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
        department_ls = []
        subject_type_ls = []
        subject_level_ls = []
        subject_semester_ls = []
        subject_graduate_ls = []
        subject_degreePoint_ls = []
        
        for page_idx in tqdm(range(page_count), '>> crawling start'):
            try:
                # 과목 크롤링
                result_box = self.driver.find_element(By.XPATH, '/html/body/div/div/div/div/section[4]/div[1]')
                result_ls = result_box.find_elements(By.TAG_NAME, 'div')
                
                for one_sbj in result_ls:
                    sbj_title = one_sbj.find_element(By.CLASS_NAME, 'title').text
                    title_ls.append(sbj_title)

                    for idx, a_tag in enumerate(one_sbj.find_elements(By.TAG_NAME, 'a')):
                        if idx == 0 : # main href
                            href_ls.append(a_tag.get_attribute('href'))
                        if idx == 2: # sub information
                            sub_info_ls = a_tag.find_elements(By.TAG_NAME, 'span')
                            for sub_idx, sub_info in enumerate(sub_info_ls):
                                if sub_idx == 0 :
                                    splited = sub_info.text.split('/')
                                    assert len(splited) == 2, print('** Error: ', splited)
                                    department = re.sub('주관 학과 : ', '', splited[0])
                                    subject_type = re.sub('교과구분 :  ', '', splited[1])
                                    
                                    department_ls.append(department)
                                    subject_type_ls.append(subject_type)
                                elif sub_idx == 2:
                                    splited = sub_info.text.split('/')
                                    assert len(splited) == 3, print('** Error: ', splited)

                                    level = re.sub('개설 학년 : ', '', splited[0])
                                    semester = re.sub('개설 학기 :  ', '', splited[1])
                                    graduate = re.sub('교과과정 :  ', '', splited[2])
 
                                    subject_level_ls.append(level)
                                    subject_semester_ls.append(semester)                                        
                                    subject_graduate_ls.append(graduate)
                                
                                elif sub_idx == 4:
                                    subject_degreePoint_ls.append(sub_info.text)


                
                # click next page
                if page_idx < page_count:
                    next_page = self.driver.find_element(By.XPATH, '/html/body/div/div/div/div/section[4]/div[2]/span[3]/a[1]')
                    next_page.click()
            except:
                title_ls.append('error')
                href_ls.append('error')
            
        
        rs['title'] = title_ls
        rs['href'] = href_ls
        rs['주관학과'] = department_ls
        rs['교과구분'] = subject_type_ls
        rs['개설 학년'] = subject_level_ls
        rs['개설 학기'] = subject_semester_ls
        rs['교과과정'] = subject_graduate_ls
        rs['학점 구조'] = subject_degreePoint_ls

        print('>> search done: ', rs.shape)

        return rs
        

    def subject_info(self, previous_rs):
        r"""
        Parameters
        ----------
        previous_rs: pd.Dataframe
            previous result
        """
        previous_rs_df = pd.read_excel(previous_rs)
        # previous_rs_df = previous_rs_df.iloc[:30, :]
        rs = pd.DataFrame()
        
        title_ls = list()
        href_ls = list()
        year_ls = list()
        semester_ls = list()
        university_ls = list()
        department_ls = list()
        profess_ls = list()
        
        for title, href in tqdm(zip(previous_rs_df['title'], previous_rs_df['href']), desc='>> crawling: '):
            self.driver.get(href)

            try:
                self.wait.until(EC.visibility_of_all_elements_located(
                    (By.XPATH, '/html/body/div/div/div/div/section[2]/div/div[4]/div/table/tbody')
                    )
                )
                recent_rs = self.driver.find_element(By.XPATH, '/html/body/div/div/div/div/section[2]/div/div[4]/div/table/tbody')
                tree_ls = recent_rs.find_elements(By.TAG_NAME, 'tr')
            except:
                title_ls.append(title)
                href_ls.append(href)
                year_ls.append('개설이력없음')
                semester_ls.append('개설이력없음')
                university_ls.append('개설이력없음')
                department_ls.append('개설이력없음')
                profess_ls.append('개설이력없음')
                continue
            

            for recent_record in tree_ls:
                td_ls = recent_record.find_elements(By.TAG_NAME, 'td')
                title_ls.append(title)
                href_ls.append(href)

                for idx, td in enumerate(td_ls):
                    if idx == 0 :
                        year_ls.append(td.text)
                    elif idx == 1:
                        semester_ls.append(td.text)
                    elif idx == 3:
                        university_ls.append(td.text)
                    elif idx == 4:
                        department_ls.append(td.text)
                    elif idx == 9:
                        profess_ls.append(td.text)
                    
        

        rs['title'] = title_ls
        rs['href'] = href_ls
        rs['강의연도'] = year_ls
        rs['학기'] = semester_ls
        rs['단과대학'] = university_ls
        rs['학과'] = department_ls
        rs['교수명'] = profess_ls

        print('>> crawling done: ', rs.shape)
        return rs

def main():
    crawler = snugenie_crawler(url='https://snugenie.snu.ac.kr')
    crawler.login(ID= os.environ.get('mysnu-id'),
          PW= os.environ.get('mysnu-pw'))
    rs = crawler.search_word('개론')
    crawler.driver.quit()

     
    today = date.today().isoformat()
    rs.to_excel(f'./result/{today}_result.xlsx', index=False)


def main2():
    crawler = snugenie_crawler(url='https://snugenie.snu.ac.kr')
    crawler.login(ID= os.environ.get('mysnu-id'),
          PW= os.environ.get('mysnu-pw'))
    rs = crawler.subject_info('./result/2023-07-15_result.xlsx')
    crawler.driver.quit()

     
    today = date.today().isoformat()
    rs.to_excel(f'./result/{today}_result2.xlsx', index=False)

    


if __name__ == '__main__':
    # main()
    main2()
    