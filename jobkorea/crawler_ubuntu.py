import os, sys, time
import copy
import warnings
import platform
import datetime
import random
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


# set utils, bot
util_path = os.pardir
if util_path not in sys.path:
    sys.path.append(os.pardir)
from utils.helper import load_config
from utils.telegram_bot import TelegramBot


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

# bot
autoBot = TelegramBot()


# 
from crawler import Crawler, Utills
from validate import Validator

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
    utils.add_empty_column(column_ls='크롤링된회사명 매출수 사원수 설립일 플랫폼입점여부 사용솔루션 채널톡사용여부'.split())

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
        
        crawled = crawler_obj.search_shopping_mall(
            shopping_mall_url = row['도메인명'],
            channel_talk = 'channel.io'
        )
        rs.loc[idx, '플랫폼입점여부'] = crawled['플랫폼입점여부']
        rs.loc[idx, '사용솔루션'] = crawled['사용솔루션']
        rs.loc[idx, '채널톡사용여부'] = crawled['채널톡사용여부']
            

        if idx % 2000 == 1999:
        # if idx == 1999:
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


def full_corporation(crawler_obj: Crawler, to_crawl_data):
    r"""crawling jobkoream, cooporation information table"""
    rs = copy.deepcopy(to_crawl_data)
    crawled_cnt = 0
    error_cnt = 0


    for idx, corp_name in tqdm(enumerate(to_crawl_data['상호'])):
        # if idx < 20:
            # autoBot.send_crawler_status(corp_name)
        crawled = crawler_obj.search_corporation_try2(corp_name)
        if type(crawled) == dict:
            rs.loc[idx, '매출수'] = crawled['매출수']
            rs.loc[idx, '사원수'] = crawled['사원수']
            rs.loc[idx, '설립일'] = crawled['설립일']
            rs.loc[idx, '크롤링된회사명'] = crawled['크롤링된 회사명']
            crawled_cnt += 1
            time.sleep(random.randint(0, 3))
        elif type(crawled) == str:
            rs.loc[idx, '매출수'] = 'error'
            rs.loc[idx, '사원수'] = 'error'
            rs.loc[idx, '설립일'] = 'error'
            rs.loc[idx, '크롤링된회사명'] = 'error'
            error_cnt += 1

        # else:
        #     pass
    
        if idx % 2000 == 1999:
            toSend = f'{autoBot.cur_time} >> 중간점검({idx})\n크롤링된 것 수: {crawled_cnt}, 에러수: {error_cnt}'
            print(toSend)
            # autoBot.send_crawler_status(toSend)
            rs.to_excel(os.path.join(Save_PATH, f'log_{idx}_corporation.xlsx'), index=False)
            time.sleep(random.randint(60, 180))
            
    
    rs.to_excel(os.path.join(Save_PATH, 'final_corporation.xlsx'), index=False)
    crawler_obj.driver.close()

    
def corporation_test(crawler_obj: Crawler, to_crawl_data):
    r"""
    headless chrome에서 table이 제대로 parsing 되지 않는 문제가 있음
    채용정보와 기업정보 테이블이 똑같이 생겨서, 헷갈려 하는데,
    --> 이 함수의 결론: 제대로 안 긁힌다
    """
    rs = copy.deepcopy(to_crawl_data)
    crawled_cnt = 0
    error_cnt = 0

    for idx, corp_name in tqdm(enumerate(to_crawl_data['상호'])):
        # if corp_name == '바오':
        if idx < 100:
            crawled = crawler_obj.search_corporation_try2(corp_name)
            # print(f'>> {corp_name}', crawled)
            if type(crawled) == dict:
                rs.loc[idx, '매출수'] = crawled['매출수']
                rs.loc[idx, '사원수'] = crawled['사원수']
                rs.loc[idx, '설립일'] = crawled['설립일']
                rs.loc[idx, '크롤링된회사명'] = crawled['크롤링된 회사명']
                crawled_cnt += 1
                time.sleep(random.randint(0, 3))
            elif type(crawled) == str:
                rs.loc[idx, '매출수'] = 'error'
                rs.loc[idx, '사원수'] = 'error'
                rs.loc[idx, '설립일'] = 'error'
                rs.loc[idx, '크롤링된회사명'] = 'error'
                error_cnt += 1
    
    rs.to_excel(os.path.join(Save_PATH, 'text__corporation.xlsx'), index=False)
    crawler_obj.driver.close()
    

def corporation_errorHandling(crawler_obj: Crawler, to_crawl_data):
    r"""에러난 것들 재확인"""
    rs = copy.deepcopy(to_crawl_data)
    crawled_cnt = 0
    error_cnt = 0

    for idx, row in tqdm(to_crawl_data.iterrows()):
        if row['매출수'] == 'error':
            corp_name = row['상호']
            crawled = crawler_obj.search_corporation_try2(corp_name)
            if type(crawled) == dict:
                rs.loc[idx, '매출수'] = crawled['매출수']
                rs.loc[idx, '사원수'] = crawled['사원수']
                rs.loc[idx, '설립일'] = crawled['설립일']
                rs.loc[idx, '크롤링된회사명'] = crawled['크롤링된 회사명']
                crawled_cnt += 1
                time.sleep(random.randint(0, 3))
            elif type(crawled) == str:
                rs.loc[idx, '매출수'] = crawled
                rs.loc[idx, '사원수'] = crawled
                rs.loc[idx, '설립일'] = crawled
                rs.loc[idx, '크롤링된회사명'] = crawled
                error_cnt += 1
        else:
            pass
        
        if idx % 2000 == 1999:
            toSend = f'{autoBot.cur_time} >> 중간점검({idx})\n크롤링된 것 수: {crawled_cnt}, 에러수: {error_cnt}'
            print(toSend)
            rs.to_excel(os.path.join(Save_PATH, f'log_{idx}_corporation.xlsx'), index=False)
            time.sleep(random.randint(60, 180))
            
    
    rs.to_excel(os.path.join(Save_PATH, 'final_corporation.xlsx'), index=False)
    crawler_obj.driver.close()


def main(arg):
    r"""main function
    Parameters
    ----------
    arg: str
        choose function to activate
    """
    print(f'>> {arg}', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

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
    elif arg == '전체 잡코리아':
        full_corporation(crawler_obj=crawler, to_crawl_data=df1)
    elif arg == '잡코리아 테스트':
        corporation_test(crawler_obj=crawler, to_crawl_data=df1)
    elif arg == '추가 크롤링: 잡코리아':
        valid = Validator(os.path.join(Save_PATH, 'final_corporation.xlsx'))
        df_error = valid.task1()
        corporation_errorHandling(crawler_obj= crawler, to_crawl_data = valid.df)
    else:
        raise NotImplementedError


if __name__ == '__main__':
    # autoBot.main()
    # main(arg='전체 크롤링: 쇼핑몰')
    # main(arg='추가 크롤링: 쇼핑몰')
    # main(arg='전체 잡코리아')
    # main(arg='잡코리아 테스트')
    main(arg='추가 크롤링: 잡코리아')