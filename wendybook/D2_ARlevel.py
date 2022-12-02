from xml.dom.pulldom import IGNORABLE_WHITESPACE
from D1_book import driver as driver 
from D1_book import per_book as PER_BOOK
import pandas as pd
import time, re, multiprocessing
from tqdm import tqdm

from selenium.common.exceptions import (NoSuchElementException,
                                        UnexpectedAlertPresentException,
                                        InvalidArgumentException
                                        )

def per_level(level, # AR레벨 
              page # 최종 페이지 수
                ):
    global driver
#     source_url = f'https://www.wendybook.com/category/levels/{level}'
    source_url = f'https://www.wendybook.com/category/levels/{level}?limit=320&did=1&page={page}'
    driver.get(source_url)
    time.sleep(3)
    
    df = pd.DataFrame(columns=['하이퍼링크', '제목'])    
    href_ls = [] ; title_ls = []
    ##### Low Performance: 8-10 it/s #####
    for row_count, prod_row in (enumerate(range(1, 81))): # 320개씩 보므로, 행은 최대 80개
        for prod_ls in range(1, 5):
            href_path = f'/html/body/div/div[4]/div[3]/div[3]/div/div[3]/div[1]/ul[{prod_row}]/li[{prod_ls}]/div[3]/a'
            title_path = f'/html/body/div/div[4]/div[3]/div[3]/div/div[3]/div[1]/ul[{prod_row}]/li[{prod_ls}]/div[1]/div[3]/strong/a'
                    # strong tag가 붙었네
                
            try:
                href = driver.find_element_by_xpath(href_path).get_attribute('href')
                title = driver.find_element_by_xpath(title_path).text
                assert re.search('[a-zA-Z]', title) != -1 , print(title, type(title), href)
                
                # crawl_count = row_count*4 + prod_ls - 1 # 이래야 첫 인덱스가 0이 됨
                # df.loc[crawl_count, '하이퍼링크'] = str(href)
                # df.loc[crawl_count, '제목'] = title
                href_ls.append(str(href)) ; title_ls.append(title)

            except NoSuchElementException:
                break
    assert len(href_ls) == len(title_ls), print(f'하이퍼링크: {len(href_ls)}, 제목 : {len(title_ls)}')
    df['하이퍼링크'] = href_ls ; df['제목']= title_ls
    df.dropna(subset=['하이퍼링크'], inplace=True)

    ##### Multiprocessing ####
    # pool = multiprocessing.Pool(4) # using 4 CPU
    

    # def page_href(product_row, # 제품이 담긴 행
    #               # product_col # 제품이 담긴 열
    #               href_rs = href_ls,
    #               title_rs = title_ls
    #               ):
    #     global driver
    #     for product_col in range(1,5):
    #         href_path = f'/html/body/div/div[4]/div[3]/div[3]/div/div[3]/div[1]/ul[{product_row}]/li[{product_col}]/div[3]/a'
    #         title_path = f'/html/body/div/div[4]/div[3]/div[3]/div/div[3]/div[1]/ul[{product_row}]/li[{product_col}]/div[1]/div[3]/strong/a'

    #         try:
    #             href = driver.find_element_by_xpath(href_path).get_attribute('href')
    #             title = driver.find_element_by_xpath(title_path).text
    #             assert re.search('[a-zA-Z]', title) != -1 , print(title, type(title), href)
        
    #         except NoSuchElementException:
    #             print(f'{prod_row}row, {prod_ls}col has a problem')
    #     # dframe.dropna(subset=['하이퍼링크'], inplace=True)
    #     # return dframe
    #     href_rs.append(str(href)) ; title_rs.append(title)

    # # if __name__ == '__main__':
    # if __name__ == 'crawler2_v0.1.py':  
    #     multiprocessing.freeze_support()
    #     ROW = range(1, 81) # 전체 행 개수는 최대 80개
    #     for row_idx in ROW:
    #         pool.starmap(page_href(row_idx), range(1,5))
    # # pool.close() ; pool.join()  #용도는 모르겠음
    # df['하이퍼링크'] = href_ls ; df['제목'] = title_ls


    '''2. 도서별 크롤링'''
    for idx, row in tqdm(df.iterrows(), desc = '각 도서별 크롤링'):
        try: 
            driver.get(row['하이퍼링크'])
            PER_BOOK(dataframe = df, index=idx)
            
        except (InvalidArgumentException, UnexpectedAlertPresentException): # 'or'을 쓰면 안됨 syntax 이슈
            print('Alert : ', row['하이퍼링크']) # 왜 발생하는거지
            try: driver.get(df.loc[idx+1, '하이퍼링크']) # 도서정보가 잘못된 하이퍼링크의 경우 driver를 기존으로 넘겨줘야함
            except InvalidArgumentException: print(df.loc[idx+1, '하이퍼링크'])
            break
    print(f'>>>>>>> [2/2] Book info collected (Lv{level})')
    
    return df.dropna(subset=['하이퍼링크'])