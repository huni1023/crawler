from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, WebDriverException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
import os, sys, time
import re
import copy
import argparse
import warnings
import math
import platform
import logging 
import pandas as pd
from tqdm import tqdm
warnings.filterwarnings('ignore')

#now we will Create and configure logger 
logging.basicConfig(filename="std.log", 
					format='%(asctime)s %(message)s', 
					filemode='w')
logger = logging.getLogger()
logger.setLevel(logging.ERROR) # error level logging
logger.propagate = False # options for no output logs to console


# set utils
util_path = os.pardir
if util_path not in sys.path:
    sys.path.append(os.pardir)
from utils.helper import load_config


Project_PATH = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
Save_PATH = os.path.join(Project_PATH, 'jobkorea', 'result')

# load config file
CONFIG_PATH = "config.yaml"
config = load_config(os.path.join(Project_PATH, 'jobkorea', CONFIG_PATH))
raw_data = pd.read_excel(config['raw_data'], engine='openpyxl')
init_url = config['init_url']
selen_path_dict = config['selen_path']
chrome_opt_dict = config['chrome_option']
solutions = config['solution']
platform_string = config['platform']

# argument
parser = argparse.ArgumentParser(description='crawling job korea')
parser.add_argument('--home', action='store_true',
                    help="crawling on home device")
parser.add_argument('--laptop', action='store_true',
                    help="crawling on laptop device")
parser.add_argument('--khrrc', action='store_true',
                    help="crawling on khrrc device")
parser.add_argument('--ubuntu', action='store_true',
                    help="crawling on ubuntu device")
parser.add_argument('--save', action='store_true',
                    help="save result")
# args = parser.parse_args('') #!# jupytor notebook case
args = parser.parse_args()


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


class Crawler:
    def __init__(self, selen_path, chromeOption, init_url, solutions, platform_string):
        r"""
        Parameters
        ----------
        selen_path: str
            path of selenium
        chromeOption: webdriver pars
            chrome browser options
        init_url : str
            initial url
        solutions: list
            list of solutions
        platform_string : list
            list of platform strings
        """
        self.driver = webdriver.Chrome(
            executable_path = selen_path, chrome_options=chromeOption
        )
        self.ACC = ActionChains(self.driver)
        self.init_url = init_url
        self.solutions = solutions
        self.platform_string = platform_string

    def get_corporation_list(self, curPageNum):
        r"""1. search corporation title in table list
        Parameters
        ----------
        corporation_count: int
            count of corporation
        """
        if curPageNum == 1:
            table_div_xpath = '//*[@id="content"]/div/div/div[1]/div/div[3]'
            tableDiv = self.driver.find_element(By.XPATH, table_div_xpath)
            tableEle = tableDiv.find_element(By.CLASS_NAME, 'list-default')
        else:
            tableEle = self.driver.find_element(By.CLASS_NAME, 'list-default')

        corp_ls_raw = tableEle.find_elements(By.TAG_NAME, 'li')
        corp_ls = [corp for corp in corp_ls_raw if 'list-post' == corp.get_attribute('class')] # li에 채용정보가 걸리기도 해서 한번 걸러줌
                    
        return corp_ls

    def get_corporation_href(self, corporation_list, search_corp_name):
        r"""get corporation element element
        Parameters
        ----------
        corporation_list: list of selenium object
        search_corp_name: str
        """
        def cleaning_string(string):
            return string.replace('㈜', '')
        
        def compare_two_string(string1, string2):
            if string1.find(' ') != -1:
                string1 = re.sub(' ', '', string1)
            elif string2.find(' ') != -1:
                string2 = re.sub(' ', '', string2)
            else:
                if string1 == string2:
                    return True
                else:
                    return False
            
            if string1 == string2:
                return True
            else:
                return False

        for corporation in corporation_list:
            a_tag = corporation.find_element(By.TAG_NAME, 'a')
            corp_name = a_tag.get_attribute('title')
            cleaned_corporation_name = cleaning_string(corp_name)
            
            if compare_two_string(search_corp_name, cleaned_corporation_name):
                return {'크롤링된 회사명': corp_name, 'href': a_tag.get_attribute('href')}
            else:
                return '이름이 일치하는 기업 없음'

    def get_next_pagination(self, curPageNum):
        r"""click next page"""
        if curPageNum == 1:
            nextBtn = self.driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/div/div/div[1]/div/div[3]/div[2]/div/div[2]/p/a')
        else:
            nextBtn = self.driver.find_element(By.XPATH, '/html/body/div/div[2]/p[2]/a') # 첫 페이지 이후부터는 페이지가 훨씬 간소화되서 제공됨, 파싱 방법이 바뀜

        href = nextBtn.get_attribute('href')
        self.driver.get(href)
        self.driver.implicitly_wait(10) # wait 10seconds


    def search_corporation(self, search_corporation):
        r"""search corporation title in jobkorea search bar and get url
        """
        def string_to_int(string):
            new_str = re.sub('[^0-9]', '', string)
            if new_str == '':
                return 0
            else:
                return int(new_str)

        def cleaning_string(string):
            return string.replace('㈜', '')
        
        def compare_two_string(string1, string2):
            if string1.find(' ') != -1:
                string1 = re.sub(' ', '', string1)
            elif string2.find(' ') != -1:
                string2 = re.sub(' ', '', string2)
            else:
                if string1 == string2:
                    return True
                else:
                    return False
            
            if string1 == string2:
                return True
            else:
                return False

        try:
            # type title text
            self.driver.get(self.init_url)
            
            # 
            inputEle = self.driver.find_element(By.XPATH, '//*[@id="stext"]')
            inputEle.send_keys(search_corporation)
            inputEle.send_keys(Keys.ENTER)
            self.driver.implicitly_wait(10) # wait 10seconds
        
            # press "기업정보" button
            buttonEle = self.driver.find_element(By.XPATH, '//*[@id="content"]/div/div/div[1]/div/div[1]/div/button[2]')
            buttonEle.click()

            # count corporation list
            count_str = self.driver.find_element(By.XPATH, '//*[@id="content"]/div/div/div[1]/div/div[3]/div[1]/p/strong').text
            searched_corp_count = string_to_int(count_str)

            # table
            tableEle = self.driver.find_element(By.XPATH, '//*[@id="content"]/div/div/div[1]/div/div[3]')
            corp_ls = tableEle.find_elements(By.TAG_NAME, 'li')

            if searched_corp_count == 0 :
                return [0, 'error'] # no need for further crawling
            else:
                for corporation in corp_ls:
                    a_tag = corporation.find_element(By.TAG_NAME, 'a')
                    corporation_name = a_tag.get_attribute('title')
                    cleaned_corporation_name = cleaning_string(corporation_name)
                    if compare_two_string(search_corporation, cleaned_corporation_name):
                        corporation_url = a_tag.get_attribute('href')
                        return [searched_corp_count, corporation_url]
                    else:
                        pass

                if searched_corp_count < 11:
                    return [searched_corp_count, 'error1']
                    
                else:
                    return [searched_corp_count, 'error2']
            
        except WebDriverException:
            return ['error', 'error']
    
    def search_corporation_try2(self, search_corporation):
        r"""상호열대치로 방법 교체
        Parameters
        ----------
        search_corporation: str
            검색할 회사명
        """
        def string_to_int(string):
            new_str = re.sub('[^0-9]', '', string)
            if new_str == '':
                return 0
            else:
                return int(new_str)
        rs = {'매출수': '', '사원수': '', '설립일': ''}
    
            
        url_template = f'https://www.jobkorea.co.kr/Search/?stext=상호&tabType=corp&Page_No=1'

        try:
            self.driver.get(url_template.replace('상호', search_corporation))
            
            # table
            tableDiv = self.driver.find_element(By.XPATH, '//*[@id="content"]/div/div/div[1]/div/div[3]')

            # count corporation list
            searched_corp_count = string_to_int(tableDiv.find_element(By.CLASS_NAME, 'dev_tot').text)

            if searched_corp_count == 0 :
                return '검색결과 없음' # no need for further crawling
            else:
                full_page_cnt = math.ceil(searched_corp_count / 10)
                if full_page_cnt == 1:
                    corp_ls = Crawler.get_corporation_list(self, 1)
                    to_crawl_corp_href = Crawler.get_corporation_href(self, corp_ls, search_corporation)

                else:
                    for idx in range(1, full_page_cnt+1):
                        corp_ls = Crawler.get_corporation_list(self, curPageNum = idx)
                        to_crawl_corp_href = Crawler.get_corporation_href(self, corp_ls, search_corporation)

                        if type(to_crawl_corp_href) == dict:
                            break
                        else:
                            Crawler.get_next_pagination(self, curPageNum = idx)

                
                if type(to_crawl_corp_href) == dict:
                    rs['크롤링된 회사명'] = to_crawl_corp_href['크롤링된 회사명']
                    self.driver.get(to_crawl_corp_href['href'])
                    self.driver.implicitly_wait(10)

                    tableEle = self.driver.find_element(By.XPATH, '//*[@id="company-body"]/div[1]/div[1]/div/table')
                    table_rows = tableEle.find_elements(By.TAG_NAME, 'tr')
                    first_three_rows = table_rows[:3]
                    
                    # parsing data
                    for idx, row in enumerate(first_three_rows):
                        if idx == 0 :
                            td_ls = row.find_elements(By.TAG_NAME, 'td')
                            for idx, td in enumerate(td_ls):
                                if idx == 1:
                                    employee_count_row = td
                                    rs['사원수'] = employee_count_row.find_element(By.CLASS_NAME, 'value').text
                        elif idx == 1:
                            td_ls = row.find_elements(By.TAG_NAME, 'td')
                            for idx, td in enumerate(td_ls):
                                if idx == 1:
                                    open_date = td
                                    rs['설립일'] = open_date.find_element(By.CLASS_NAME, 'value').text
                        elif idx == 2:
                            td_ls = row.find_elements(By.TAG_NAME, 'td')
                            for idx, td in enumerate(td_ls):
                                if idx == 1:
                                    sales = td
                                    rs['매출수'] = sales.find_element(By.CLASS_NAME, 'value').text
                    return rs
                elif type(to_crawl_corp_href) == str:
                    return to_crawl_corp_href
                else:
                    raise NotImplementedError

        except NoSuchElementException as e:
            logger.error('noSuchElement')
            # self.driver.quit()
            return 'error'

        except WebDriverException as e:
            logger.error('webdriverError')
            # self.driver.quit()
            return 'error'


    def search_corporation_info(self, href):
        r"""search corporation information table
        """
        try:
            self.driver.get(href)
            tableEle = self.driver.find_element(By.XPATH, '//*[@id="company-body"]/div[1]/div[1]/div/table')
            table_rows = tableEle.find_elements(By.TAG_NAME, 'tr')
            first_three_rows = table_rows[:3]
            
            # parsing data
            rs = {'매출수': '', '사원수': '', '설립일': ''}
            for idx, row in enumerate(first_three_rows):
                if idx == 0 :
                    td_ls = row.find_elements(By.TAG_NAME, 'td')
                    for idx, td in enumerate(td_ls):
                        if idx == 1:
                            employee_count_row = td
                            rs['사원수'] = employee_count_row.find_element(By.CLASS_NAME, 'value').text
                elif idx == 1:
                    td_ls = row.find_elements(By.TAG_NAME, 'td')
                    for idx, td in enumerate(td_ls):
                        if idx == 1:
                            open_date = td
                            rs['설립일'] = open_date.find_element(By.CLASS_NAME, 'value').text
                elif idx == 2:
                    td_ls = row.find_elements(By.TAG_NAME, 'td')
                    for idx, td in enumerate(td_ls):
                        if idx == 1:
                            sales = td
                            rs['매출수'] = sales.find_element(By.CLASS_NAME, 'value').text
            return rs
                

        except WebDriverException as e:
            print('>*>* error: ', e)
            # self.driver.save_screenshot(os.path.join(Save_PATH, 'screen_shot.png'))
            return {'매출수': 'error', '사원수': 'error', '설립일': 'error'}


    def search_shopping_mall(self, shopping_mall_url, channel_talk):
        r"""search if solution and platform
        Parameters
        ----------
        shopping_mall_url: str
            url of shopping mall
        channel_talk: str
            whether channel talk is existed or not
        """
        result = {'플랫폼입점여부': '', '사용솔루션': '', '채널톡사용여부': ''}

        # enter url
        try:            
            self.driver.get(url = shopping_mall_url)
            html = self.driver.page_source
            
            # search channel talk
            if html.find(channel_talk) != -1:
                result['채널톡사용여부'] += 'Y' 
        
            else:
                result['채널톡사용여부'] += 'N'

            # search solution
            for solution, search_str in self.solutions.items():
                if html.find(search_str) != -1:
                    if len(result['사용솔루션']) == 0:
                        result['사용솔루션'] += solution
                    else:
                        multi_solution = ', ' + solution
                        result['사용솔루션'] += multi_solution
                else:
                    pass
                
            # in case of nothing
            if result['사용솔루션'] == '':
                result['사용솔루션'] = 'N'
            
            # search platform
            for platform in self.platform_string:
                if html.find(platform) != -1:
                    result['플랫폼입점여부'] += 'Y'
                    break 
                else:
                    pass
            # in case of nothing
            if result['플랫폼입점여부'] == '':
                result['플랫폼입점여부'] += 'N'

            return result
        except WebDriverException:
            result['플랫폼입점여부'] = 'error'
            result['사용솔루션'] = 'error'
            result['채널톡사용여부'] = 'error'
            return result
    

    def test_driver(self):
        r"""test function: chrome webdriver"""
        self.driver.get('https://www.naver.com')
        if 'https://www.naver.com/' == self.driver.current_url:
            return print('>> test passed: chrome webdriver')
        else:
            raise ValueError('** test failed: chrome webdriver')

class Utills:
    def __init__(self, raw_data):
        r"""helper function cleaning data"""
        self.raw_data = raw_data

    def clear_useless_text(self, column_name):
        r"""cleaning useless text
        Parameters
        ----------
        column_name: str
        """
        self.raw_data[column_name].apply(lambda x: re.sub('', '', x))
        return self.raw_data['상호']

    def add_empty_column(self, column_ls):
        r"""add empty column for further processing
        column_ls: list
            list of columns to be entered
        """
        # add text column
        rs = copy.deepcopy(self.raw_data)
        for column in column_ls:
            rs[column] = '' 
        
        self.cleaned_data = rs
        return rs

    
    def cleanUrl(self):
        r"""cleaning url
        Parameters
        ----------
        """
        rs = copy.deepcopy(self.raw_data)
        new_url_ls = list()
        for url in rs['도메인명']:
            if url.find('http') != -1:
                # case1. http
                if url[:7] == 'http://':
                    new_url_ls.append('https://' + url[7:])
                else:
                    new_url_ls.append(url)
            
            # case2. no http
            else:
                new_url_ls.append('https://' + url)
        
        rs['도메인명'] = new_url_ls
        self.cleaned_data = rs
        return rs

    def compare_progress(self, target, interrupted_data, column):
        r"""compare target and interrupted result and generate which is left
        target : str
            data path to target data
        interrupted_data: str
            data path to interrupted data
        column : str
            which column should be used as a comparison criteria 
        """
        df_target = pd.read_excel(target)
        df_interrupted = pd.read_excel(interrupted_data)
        # find first row where NaN exists
        threshold = 0 #!#
        
        # and then cut the df_target
        return df_target.iloc[threshold, :]

    # def create_zip(self, file_name, full_directory):
    #     r"""Simple function create zip files
    #     """
    #     shutil.make_archive(file_name, 'zip', full_directory)
    


if __name__ == '__main__':
    if args.home:
        crawler = Crawler(selen_path = selen_path_dict['home'],
                          chromeOption=chrome_opt,
                          init_url=init_url,
                          solutions = solutions,
                          platform_string = platform_string)
    elif args.laptop:
        crawler = Crawler(selen_path = selen_path_dict['laptop'],
                          chromeOption=chrome_opt,
                          init_url=init_url,
                          solutions = solutions,
                          platform_string = platform_string)
    elif args.khrrc:
        crawler = Crawler(selen_path = selen_path_dict['khrrc'],
                          chromeOption=chrome_opt,
                          init_url=init_url, 
                          solutions = solutions,
                          platform_string = platform_string)
    elif args.ubuntu:
        crawler = Crawler(selen_path= selen_path_dict['ubuntu'],
                    chromeOption = chrome_opt,
                    init_url = init_url,
                    solutions =solutions,
                    platform_string = platform_string)
        crawler.test_driver()

        utils = Utills(raw_data = raw_data)
        utils.cleanUrl()
        
    else:
        raise NotImplementedError
    