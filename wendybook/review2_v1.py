from doctest import testfile
import os, re, time
import pandas as pd
from sys import platform
from tqdm import tqdm

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (NoSuchElementException,
                                        UnexpectedAlertPresentException,
                                        ElementClickInterceptedException
                                        )

chrome_opt = webdriver.ChromeOptions() 
chrome_opt.add_experimental_option('excludeSwitches', ['enable-logging']) # window specific error

print('Current OS : ', platform)
if 'darwin' in platform:
    selen_path = '/Users/huni/Dropbox/내 Mac (MacBook-Pro.local)/Downloads/chromedriver'
    chrome_opt.add_argument('--kiosk')

elif 'win32' in platform:
    selen_path = r'C:\Users\jhun1\Dropbox\My PC (LAPTOP-VLNR6K8R)\Downloads\chromedriver_win32\chromedriver'
    chrome_opt.add_argument('--start-maximized')

driver = webdriver.Chrome(executable_path = selen_path, chrome_options=chrome_opt)


'''Django Charlist 특성상 열을 길게 빼면 별로고, long form으로 쌓음'''
def review_crawler(dframe, # 앞에서 정리된 데이터프레임
                   save_dir, # 저장경로,
                   test_opt = False, # 테스트용 옵션
                   devide_opt = False, # 잘라서 크롤링할 때
                   start = 0, # 잘라서 크롤링할 때
                   end = 0 # 잘라서 크롤링할 때
                ):
    global driver
    temp_dict = {'하이퍼링크': [],
                '제목': [],
                '별점': [],
                '상품평': [],
                '도움': []
                }
    if test_opt == True: dframe = dframe.iloc[:10, :] # 시범용 
    if devide_opt == True: 
        print(f'>>>> Crawling from {start} to {end}')
        dframe = dframe.iloc[start : end, :] 

    for hyper_link, title in tqdm(zip(dframe['하이퍼링크'].values, dframe['제목'].values)):
        driver.get(hyper_link) ; time.sleep(1) # 이미지 로드 떄문에 시간이 좀 걸릴 때가 있음

        '''최종으로는 이걸 상품평 20개 넘을 때 판단하는 코드를 추가하면 됨'''
        try:
            Review_box = driver.find_element_by_xpath('/html/body/div[1]/div[4]/div[2]/div/div/div/div/div[2]/div[3]/div[2]/ul')
        except NoSuchElementException: # https://www.wendybook.com/book/detail/99796
            Review_box = driver.find_element_by_class_name('reViewList')

        # 별점        
        star_box = Review_box.find_elements_by_class_name('icon_star')
        star_ls = []
        for star in star_box: 
            width = star.find_element_by_css_selector('em').get_attribute('style')
            star = int(
                        ''.join(
                            re.findall('[0-9]', width)
                        )
                    )/20
            star_ls.append(star)

        # 상품평
        review_box = Review_box.find_elements_by_class_name('reViewCon')
        review_ls = []
        for review in review_box: 
            review_ls.append(review.find_element_by_css_selector('p').text)
        
        # 도움
        help_box = Review_box.find_elements_by_class_name('replyCheckBox')
        help_ls = []
        for helpp in help_box:
            help_cnt = helpp.find_element_by_class_name('recommend-cnt').text
            help_ls.append(help_cnt)


        # 최종 넣어주는 코드
        for star, review, help_cnt in zip(star_ls, review_ls, help_ls):
            temp_dict['하이퍼링크'].append(hyper_link)
            temp_dict['제목'].append(title)
            temp_dict['별점'].append(star)
            temp_dict['상품평'].append(review)
            temp_dict['도움'].append(help_cnt)
    
    df = pd.DataFrame.from_dict(temp_dict)
    tot_save_path = os.path.join(os.getcwd(), save_dir, f'wendybook_review_{start}_{end}.xlsx')
    return df.to_excel(tot_save_path)

#### 리뷰 페이지 넘기는게 안되고 있음
# driver.get('https://www.wendybook.com/book/detail/125682/')
# time.sleep(1)
# Page_area = driver.find_element_by_class_name('PageArea')
# for idx in range(2, 50):
#     try:
#         # next_page = Page_area.find_element_by_partial_link_text(str(idx))
#         # next_page_url = next_page.get_attribute('href')
#         next_page = Page_area.find_element_by_css_selector('a.mgL20 > img')
#         time.sleep(2) # for waiting clickable
#         try:
#             next_page.click() 
#         except ElementClickInterceptedException:
#             # driver.execute_script("window.scrollTo(0, 100)")
#             ActionChains(driver).send_keys(Keys.PAGE_DOWN).perform()
#             next_page = Page_area.find_element_by_css_selector('a.mgL20 > img')
#             ActionChains(driver).send_keys(Keys.PAGE_DOWN).perform()
#             next_page.click()


#     except NoSuchElementException:
#         # print('여기서 멈춤', idx)
#         break
if __name__ == '__main__':
    if ('TEST1' not in os.getcwd()) and ('Cury_tech' in os.getcwd()):
        Excel_name = 'wendybook_cleaned.xlsx'
        # print('부모: ',os.pardir)
        parent_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
        # print(parent_dir)
        excel_path = os.path.join(parent_dir, 'Recommendation_system',
                                    'TEST1', 
                                    Excel_name)


    RS_crawler = pd.read_excel(excel_path)

    # 22.01.17: 1000개 돌리는데 30분 정도 걸림
    review_crawler(RS_crawler,
                    save_dir= 'RESULT_review',
                    # test_opt = True # 빨리 LDA 코드 만들어야 함
                    devide_opt= True,
                    start = 6000,
                    end = RS_crawler.shape[0]
                    )