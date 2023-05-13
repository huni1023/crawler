import os, sys, time
import copy
import warnings
import platform
import datetime
import pandas as pd
from tqdm import tqdm
warnings.filterwarnings('ignore')

from selenium import webdriver


# assert system
if platform.system() != "Linux":
    raise KeyError('>> check your platform')

# set dir
Project_PATH = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
Save_PATH = os.path.join(Project_PATH, 'jobkorea', 'result')


# set utils
util_path = os.pardir
if util_path not in sys.path:
    sys.path.append(os.pardir)
from utils.helper import load_config

# load config file
CONFIG_PATH = "config.yaml"
config = load_config(os.path.join(Project_PATH, 'jobkorea', CONFIG_PATH))
raw_data = pd.read_excel(config['raw_data'], engine='openpyxl')
init_url = config['init_url']
selen_path_dict = config['selen_path']
chrome_opt_dict = config['chrome_option']
solutions = config['solution']
platform_string = config['platform']
crawled_data = pd.read_excel(os.path.join(Save_PATH, 'cleaned_230428.xlsx'), engine='openpyxl')

# 
from crawler import Crawler, Utills

# chrome option
chrome_opt = webdriver.ChromeOptions()
for _ in chrome_opt_dict['default']:
    chrome_opt.add_argument(_)

for _ in chrome_opt_dict['headless']:
    chrome_opt.add_argument(_)
chrome_opt.add_argument(f'user-agent={chrome_opt_dict["user_agent"]}')


def cleaning_data():
    r"""cleaning data"""
    utils = Utills(raw_data= raw_data)
    utils.add_empty_column(column_ls='매출수 사원수 설립일 플랫폼입점여부 사용솔루션 채널톡사용여부'.split())

    return utils.cleanUrl()

def compare_data(raw_data, crawled_data, compared_col):
    r"""Compare raw data with previously cralwed
    subtract already crawled data
    Parameters
    ----------
    raw_data: pd.Dataframe

    crawled_data: pd.Dataframe

    compared_col: list
        list of column which added and compared
    """
    rs = copy.deepcopy(raw_data)
    
    for col in compared_col:
        rs[col] = crawled_data[col]

    return rs

def full_crawling(crawler_obj, to_crawl_data):
    r"""쇼핑몰: 덜 크롤링된것들 다시 크롤링함]
    Parameters
    ----------
    crawler_obj: selenium webdriver
    to_crawl_data: pd.Dataframe
    """
    rs = copy.deepcopy(to_crawl_data)

    for idx, row in tqdm(to_crawl_data.iterrows()):
        if idx < 20:
            crawled = crawler_obj.search_shopping_mall(
                shopping_mall_url = row['도메인명'],
                channel_talk = 'channel.io'
            )
            rs.loc[idx, '플랫폼입점여부'] = crawled['플랫폼입점여부']
            rs.loc[idx, '사용솔루션'] = crawled['사용솔루션']
            rs.loc[idx, '채널톡사용여부'] = crawled['채널톡사용여부']
            

        # if idx % 2000 == 1999:
        if idx == 1999:
            rs.to_excel(os.path.join(Save_PATH, f'log_{idx}_shoppingmall.xlsx'), index=False)
            print(f'>> 중간저장: {idx}', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    rs.to_excel(os.path.join(Save_PATH, 'final_shoppingmall.xlsx'), index=False)
    crawler_obj.driver.close()

def additional_crawling(crawler_obj, to_crawl_data):
    r"""쇼핑몰: 덜 크롤링된것들 다시 크롤링함]
    Parameters
    ----------
    crawler_obj: selenium webdriver
    to_crawl_data: pd.Dataframe
    """
    rs = copy.deepcopy(to_crawl_data)

    for idx, row in tqdm(to_crawl_data.iterrows()):
        if idx < 50:
            # if (row['플랫폼입점여부'] == 'error') and (row['사용솔루션'] == 'error') and (row['채널톡사용여부'] == 'error'):
            if row['플랫폼입점여부'] == 'error':
                crawled = crawler_obj.search_shopping_mall(
                    shopping_mall_url = row['도메인명'],
                    channel_talk = 'channel.io'
                )
                rs.loc[idx, '플랫폼입점여부'] = crawled['플랫폼입점여부']
                rs.loc[idx, '사용솔루션'] = crawled['사용솔루션']
                rs.loc[idx, '채널톡사용여부'] = crawled['채널톡사용여부']
            else: pass

        if idx % 2000 == 1999:
            rs.to_excel(os.path.join(Save_PATH, f'log_{idx}_shoppingmall.xlsx'), index=False)
            print(f'>> 중간저장: {idx}', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    crawler_obj.driver.close()

def main(arg):
    r"""main function
    Parameters
    ----------
    arg: str
        choose function to activate
    """
    print('>> 쇼핑몰 추가 크롤링', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    # define class
    crawler = Crawler(selen_path= selen_path_dict['ubuntu'],
            chromeOption = chrome_opt,
            init_url = init_url,
            solutions =solutions,
            platform_string = platform_string)
    crawler.test_driver()
    df1 = cleaning_data()

    df2 = compare_data(raw_data= df1,
                crawled_data= crawled_data,
                compared_col='플랫폼입점여부 사용솔루션 채널톡사용여부'.split()
                )

    if arg == '추가 크롤링: 쇼핑몰':
        additional_crawling(crawler, to_crawl_data = df2)
    elif arg == '전체 크롤링: 쇼핑몰':
        full_crawling(crawler, to_crawl_data = df1)
    else:
        raise NotImplementedError


if __name__ == '__main__':
    main(arg='전체 크롤링: 쇼핑몰')
    # main(arg='추가 크롤링: 쇼핑몰')