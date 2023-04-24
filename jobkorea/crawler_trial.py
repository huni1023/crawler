from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
import os, sys, time
import re
import argparse
import warnings
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
selen_path_dict = config['selen_path']
init_url = config['init_url']

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
args = parser.parse_args()

# chrome option
chrome_opt = webdriver.ChromeOptions()
prefs = {"profile.managed_default_content_settings.images": 2}
chrome_opt.add_experimental_option("prefs", prefs) 
chrome_opt.add_experimental_option("detach", True) # prevent automatically closed tab
chrome_opt.add_experimental_option("excludeSwitches", ["enable-logging"])


class Crawler:
    def __init__(self, selen_path, chromeOption, init_url):
        r"""
        Parameters
        ----------
        selen_path: str
            path of selenium
        chromeOption: webdriver pars
            chrome browser options
        init_url : str
            initial url
        """
        self.driver = webdriver.Chrome(
            executable_path = selen_path, chrome_options=chromeOption
        )
        self.ACC = ActionChains(self.driver)
        self.init_url = init_url
    
    def init_table_setting(self, tag: str):
        r"""crawling corportaion information
        Parameters
        ----------
        tag: str
            corporation type string
        """
        self.driver.get(self.init_url)
        time.sleep(2)
        tagBox = self.driver.find_element(By.XPATH, '//*[@id="anchorGICnt_1"]')
        tag_ls = tagBox.find_elements(By.TAG_NAME, "li")
        
        for idx, each_tag_li in enumerate(tag_ls):
            each_tag = each_tag_li.find_element(By.XPATH, f'//*[@id="anchorGICnt_1"]/li[{idx+1}]/button/span').text
            if each_tag == tag:
                each_tag_li.click()
                # count = each_tag_li.find_element(By.TAG_NAME, 'em').text
                # print(re.sub('^[0-9]', '', count))

        #!# corporation count setting should be updated

        corporation_table = self.driver.find_element(By.XPATH, '//*[@id="dev-gi-list"]/div/div[5]/table/tbody')
        corporation_rows = corporation_table.find_elements(By.TAG_NAME, 'tr')

        corp_dict = {'title': list(),'link': list()}
        for idx, each_corporation in enumerate(corporation_rows):
            corp_title_ele = each_corporation.find_element(By.CLASS_NAME, 'tplCo')
            corp_href = corp_title_ele.find_element(By.TAG_NAME, 'a').get_attribute('href')
            # print('>> goal: ', corp_href)
            corp_dict['title'].append(corp_title_ele.text)
            corp_dict['link'].append(corp_href)

        
        return pd.DataFrame.from_dict(corp_dict)
    
    def D2(self, ):
        return NotImplementedError

    def quit(self):
        r"""A simple function to quit driver
        
        """
        self.driver.quit()
    

if __name__ == '__main__':
    if args.home:
        crawler = Crawler(selen_path = selen_path_dict['home'],
                          chromeOption=chrome_opt,
                          init_url=init_url)
    elif args.laptop:
        crawler = Crawler(selen_path = selen_path_dict['laptop'],
                          chromeOption=chrome_opt,
                          init_url=init_url)
    elif args.khrrc:
        crawler = Crawler(selen_path = selen_path_dict['khrrc'],
                          chromeOption=chrome_opt,
                          init_url=init_url)
    else:
        raise NotImplementedError
    
    df = crawler.init_table_setting(tag = '외국계')
    
    if args.save:
        df.to_excel(os.path.join(Project_PATH, 'jobkorea', 'result', 'pilot.xlsx'))
    # crawler.quit()
    



