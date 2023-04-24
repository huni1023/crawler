from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, WebDriverException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
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
args = parser.parse_args('')


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

    def search_corporation(self):
        r"""search corporation title in search bar
        """
        # type title text
        # //*[@id="stext"]

        # press enter
        # press "기업정보" button
        # if empty: type NaN
        # else if(list less than 10): find match list in xlsx
        # else if(list more than 10): press next page and find match list in xlsx --> 차라리 일단 패스하는게..
        pass

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
            for solution in solutions:
                if html.find(solution) != -1:
                    if len(result['사용솔루션']) == 0:
                        result['사용솔루션'] += solution
                    else:
                        multi_solution = ', ' + solution
                        result['사용솔루션'] += multi_solution
                else:
                    result['사용솔루션'] = 'N'
            
            return result
        except WebDriverException:
            result['사용솔루션'] = 'error'
            result['채널톡사용여부'] = 'error'
            return result
        


class Utills:
    def __init__(self, raw_data):
        self.raw_data = raw_data

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
    