from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, WebDriverException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
import os, sys, time
import re
import copy
import argparse
import warnings
import shutil
import pandas as pd
from tqdm import tqdm
warnings.filterwarnings('ignore')


# set utils
util_path = os.pardir
if util_path not in sys.path:
    sys.path.append(os.pardir)
from utils.helper import load_config


# load config file
Project_PATH = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
CONFIG_PATH = "config.yaml"
config = load_config(os.path.join(Project_PATH, 'jobkorea', CONFIG_PATH))
raw_data = pd.read_excel(config['raw_data'], engine='openpyxl')
init_url = config['init_url']
selen_path_dict = config['selen_path']
solutions = config['solution']

# argument
parser = argparse.ArgumentParser(description='crawling job korea')
parser.add_argument('--home', action='store_true',
                    help="crawling on home device")
parser.add_argument('--laptop', action='store_true',
                    help="crawling on laptop device")
parser.add_argument('--khrrc', action='store_true',
                    help="crawling on khrrc device")
parser.add_argument('--save', action='store_true',
                    help="save result")
args = parser.parse_args('') #!# jupytor notebook case
# args = parser.parse_args()


# chrome option
chrome_opt = webdriver.ChromeOptions()
prefs = {"profile.managed_default_content_settings.images": 2}
chrome_opt.add_experimental_option("prefs", prefs) 
chrome_opt.add_experimental_option("detach", True) # prevent automatically closed tab
chrome_opt.add_experimental_option("excludeSwitches", ["enable-logging"])


class Crawler:
    def __init__(self, selen_path, chromeOption, init_url, solutions):
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
        """
        self.driver = webdriver.Chrome(
            executable_path = selen_path, chrome_options=chromeOption
        )
        self.ACC = ActionChains(self.driver)
        self.init_url = init_url
        self.solutions = solutions

    def search_corporation(self, search_corporation ):
        r"""search corporation title in search bar
        """
        def string_to_int(string):
            new_str = re.sub('^[0-9]', '', string)
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
            self.driver.find_element(By.XPATH, '//*[@id="stext"]')
            self.driver.send_keys(search_corporation)
            self.driver.send_keys(Keys.ENTER)
            self.driver.implicitly_wait(10) # wait 10seconds
        
            # press "기업정보" button
            buttonEle = self.driver.find_element(By.XPATH, '//*[@id="content"]/div/div/div[1]/div/div[1]/div/button[2]')
            buttonEle.click()

            # count corporation list
            count_str = self.driver.find_element(By.XPATH, '//*[@id="content"]/div/div/div[1]/div/div[2]/div[1]/p/strong').text
            searched_corp_count = string_to_int(count_str)

            # table
            tableEle = self.driver.find_element(By.XPATH, '//*[@id="content"]/div/div/div[1]/div/div[2]/div[2]/div/div[1]/ul')
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
    
    def search_corporation_info(self, href):
        r"""search corporation information
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
                

        except WebDriverException:
            return {'매출수': 'error', '사원수': 'error', '설립일': 'error'}


    def search_channel_and_solution(self, shopping_mall_url, channel_talk):
        r"""search if solution and platform
        Parameters
        ----------
        shopping_mall_url: str
            url of shopping mall
        channel_talk: str
            whether channel talk is existed or not
        """
        result = {'사용솔루션': '', '채널톡사용여부': ''}

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
                print('>> search_string: ', search_str)
                if html.find(search_str) != -1:
                    print('>> success search: ', solution)
                    if len(result['사용솔루션']) == 0:
                        result['사용솔루션'] += solution
                    else:
                        multi_solution = ', ' + solution
                        result['사용솔루션'] += multi_solution
                else:
                    pass
                
                # in case of nothing
                if len(result['사용솔루션']) == 0:
                    result['사용솔루션'] = 'N'
            return result
        except WebDriverException:
            result['사용솔루션'] = 'error'
            result['채널톡사용여부'] = 'error'
            return result
        


class Utills:
    def __init__(self, raw_data):
        self.raw_data = raw_data

    def clear_useless_text(self, column_name):
        r"""cleaning useless text
        Parameters
        ----------
        column_name: str
        """
        self.raw_data[column_name].apply(lambda x: re.sub('', '', x))

    def add_empty_column(self, column_ls):
        r"""add empty column for further processing
        column_ls: list
            list of columns to be entered
        """
        # add text column
        rs = copy.deepcopy(self.raw_data)
        for column in column_ls:
            rs[column] = '' 
        
        return rs

    def cleaning_url(self, data):
        r"""add https:// in url
        Parameters
        ----------
        data: pd.Dataframe
            pandas dataframe
        """
        rs = copy.deepcopy(data)
        new_url_ls = list()
        for url in rs['도메인명']:
            if url[:8] != 'https://':
                new_url_ls.append('https://' + url)
            elif url[:7] == 'http://':
                new_url_ls.append('https://' + url)
            else:
                new_url_ls.append(url)
        
        rs['도메인명'] = new_url_ls
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
                          solutions = solutions)
    elif args.laptop:
        crawler = Crawler(selen_path = selen_path_dict['laptop'],
                          chromeOption=chrome_opt,
                          init_url=init_url,
                          solutions = solutions)
    elif args.khrrc:
        crawler = Crawler(selen_path = selen_path_dict['khrrc'],
                          chromeOption=chrome_opt,
                          init_url=init_url, 
                          solutions = solutions)
    else:
        raise NotImplementedError
    