# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

import os, re 
import pandas as pd
from sys import platform

chrome_opt = webdriver.ChromeOptions() 

prefs = {"profile.managed_default_content_settings.images": 2} # to unable image
chrome_opt.add_experimental_option("prefs", prefs)
chrome_opt.add_experimental_option('excludeSwitches', ['enable-logging'])

print('Current OS : ', platform)
if 'darwin' in platform:
    selen_path = '/Users/huni/Dropbox/내 Mac (MacBook-Pro.local)/Downloads/chromedriver'
    chrome_opt.add_argument('--kiosk')

elif 'win32' in platform:
    selen_path = r'C:\Users\jhun1\Dropbox\My PC (LAPTOP-VLNR6K8R)\Downloads\chromedriver_win32\chromedriver'
    chrome_opt.add_argument('--start-maximized')


driver = webdriver.Chrome(executable_path = selen_path, chrome_options=chrome_opt)
'''
1. 도서제목
2. 상품평개수
3. 가격
4. 형태
5. 출판사
6. 작가
7. ISBN
8. 도서정보 페이지
9. 대상연력
10. 주제
11. 분야
12. 시리즈
13. 수상/추천
14. AR
15. Lexile, 수상/추천...
16. 도서 이미지
'''
### TEST1 ###
# 이 링크의 정보를 모두 얻으시오: https://www.wendybook.com/book/detail/162095
# 가격을 포함하여 다른 정보 모두 얻을 수 있어야 함

### TEST2 ###
# 이 링크의 정보를 모두 얻으시오: https://www.wendybook.com/book/detail/164097
# 표에 다 얻어져야함


def per_book(dataframe, index):
    global driver
    title_path = '/html/body/div/div[4]/div[2]/div/div/div/div/div[1]/div[1]/div[2]/div[1]/strong'
    title = driver.find_element_by_xpath(title_path).text
    if dataframe.loc[index , '제목'] != None:
        if dataframe.loc[index , '제목'][:5] != title[:5]: # 약간 씩 변용이 있어서, 앞의 5개 글자의 일치 여부만 확인함
            print(dataframe.loc[index , '제목'], ':vs:', title)
            pass

    # 상품평개수       
    review_path = '/html/body/div/div[4]/div[2]/div/div/div/div/div[1]/div[1]/div[2]/div[1]/div[3]/a[1]/span/span'
    review_count = driver.find_element_by_xpath(review_path).text
    dataframe.loc[index, '상품평개수'] = int(review_count)


    # 가격
    try: # 일반가격이 있는 형태(예시): https://www.wendybook.com/book/detail/108218
        bef_prc_path = '/html/body/div/div[4]/div[2]/div/div/div/div/div[1]/div[1]/div[2]/div[2]/div/b'
        bef_prc = driver.find_element_by_xpath(bef_prc_path).text
        
        aft_prc_path = '/html/body/div/div[4]/div[2]/div/div/div/div/div[1]/div[1]/div[2]/div[2]/div/div/span[1]'
        aft_prc = driver.find_element_by_xpath(aft_prc_path).text
        HTML_setting = 'Normal' # 대부분의 도서는 이 코드에서 긁힘
    
    except NoSuchElementException: #표형태의 가격이 있는 형태(예시): https://www.wendybook.com/book/detail/162095
        try: 
            bef_prc_path = '/html/body/div/div[4]/div[2]/div/div/div/div/div[1]/div[1]/div[2]/div[2]/table/tbody/tr[1]/td/span'
            bef_prc = driver.find_element_by_xpath(bef_prc_path).text

        except NoSuchElementException: # 태그 끝이 span이 아닌 div인 경우: https://www.wendybook.com/book/detail/161798
            bef_prc_path = '/html/body/div/div[4]/div[2]/div/div/div/div/div[1]/div[1]/div[2]/div[2]/table/tbody/tr[2]/td/div'
            bef_prc = driver.find_element_by_xpath(bef_prc_path).text
        
        try:
            aft_prc_path = '/html/body/div/div[4]/div[2]/div/div/div/div/div[1]/div[1]/div[2]/div[2]/table/tbody/tr[2]/td/span'
            aft_prc = driver.find_element_by_xpath(aft_prc_path).text
        except NoSuchElementException: # 태그 끝이 span이 아닌 div인 경우: https://www.wendybook.com/book/detail/161798
            aft_prc_path = '/html/body/div/div[4]/div[2]/div/div/div/div/div[1]/div[1]/div[2]/div[2]/table/tbody/tr[3]/td/div[1]/div'
            aft_prc = driver.find_element_by_xpath(aft_prc_path).text
        HTML_setting = 'abNormal' # 매우 소수의 도서는 이 코드에서 긁힘

    # 왜 이런 if문이 있는지 궁금하다면..  둘을 비교해보세요
    # https://www.wendybook.com/book/detail/21732 
    # https://www.wendybook.com/book/detail/11592
    bef_prc_int = int(''.join(re.findall('[0-9]', bef_prc)))
    aft_prc_int = int(''.join(re.findall('[0-9', aft_prc)))
    if bef_prc_int > aft_prc_int: 
        dataframe.loc[index, '할인 전 가격'] = bef_prc_int
        dataframe.loc[index, '할인 후 가격'] = aft_prc_int
    elif bef_prc_int < aft_prc_int:
        dataframe.loc[index, '할인 전 가격'] = aft_prc_int
        dataframe.loc[index, '할인 후 가격'] = bef_prc_int


    for i in range(1, 8):
        try: # 첫번째, 두번째 테이블의 항목 개수는 유동적이므로 try, except 활용
            if HTML_setting == 'Normal':
                div_idx = 2
            elif HTML_setting == 'abNormal':
                div_idx = 3
            try:
                Fir_tb =  f'/html/body/div/div[4]/div[2]/div/div/div/div/div[1]/div[1]/div[2]/div[{div_idx}]/table/tbody/tr[{i}]/th'
            except NoSuchElementException: # https://www.wendybook.com/book/detail/153560 
                Fir_tb = f'/html/body/div/div[4]/div[2]/div/div/div/div/div[1]/div[1]/div[2]/div[{div_idx}]/table/tbody/tr[{i}]/td/div'
            Fir_tb_label = driver.find_element_by_xpath(Fir_tb).text
            if Fir_tb_label == '행사가': break # 행사가까지 수집할 필요 없음

            cont = f'/html/body/div/div[4]/div[2]/div/div/div/div/div[1]/div[1]/div[2]/div[{div_idx}]/table/tbody/tr[{i}]/td'
            cont_ = driver.find_element_by_xpath(cont).text
            dataframe.loc[index, Fir_tb_label] = cont_
            
            Sec_tb = f'/html/body/div/div[4]/div[2]/div/div/div/div/div[1]/div[1]/div[2]/div[{div_idx+1}]/table/tbody/tr[{i}]/th'
            Sec_tb_label = driver.find_element_by_xpath(Sec_tb).text
                
            cont_final = []
            for j in range(1, 3): # 각각의 하이퍼링크가 별도의 태그 안에 숨어 있는 경우가 있어서 다시 for loop를 돌림
                try:
                    cont2 = f'/html/body/div/div[4]/div[2]/div/div/div/div/div[1]/div[1]/div[2]/div[{div_idx+1}]/table/tbody/tr[{i}]/td/a[{j}]'
                    cont_2 = driver.find_element_by_xpath(cont2).text
                    cont_final.append(cont_2) 

                except NoSuchElementException:
                    break
            
            cont_final = ', '.join(cont_final)
            # print(ttt, " ::: ", cont_final)
            dataframe.loc[index, Sec_tb_label] = cont_final

        except NoSuchElementException:
            break

    return dataframe