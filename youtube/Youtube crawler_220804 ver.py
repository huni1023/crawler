#20220804 ver
#import 함수

from selenium import webdriver as wd
from bs4 import BeautifulSoup
import time
import csv

driver = wd.Chrome(executable_path="C:\Download\chromedriver.exe")
url = 'https://www.youtube.com/watch?v=3QoUKVlRGf0'
driver.get(url)

#스크롤 함수지정 - 댓글 불러오는 속도가 원활하다면 더 간단하게 처리
def scroll(driver, scroll_time, wait_time):
    last_page_height = driver.execute_script(
        "return document.documentElement.scrollHeight"
    )

    stand_height = 0
    sub_height = last_page_height
    while True:

        current_height = driver.execute_script(
            "return document.documentElement.scrollHeight"
        )

        for i in range(10):
            driver.execute_script(
                f"window.scrollTo(0, {stand_height + (sub_height/10 * i)});"
            )
            time.sleep(scroll_time)
        time.sleep(wait_time)

        new_page_height = driver.execute_script(
            "return document.documentElement.scrollHeight"
        )
        stand_height = last_page_height
        sub_height = new_page_height - last_page_height

        if new_page_height == last_page_height:
            break
        last_page_height = new_page_height
        time.sleep(wait_time)


##스크롤링
scroll(driver, 3, 1)
time.sleep(2)


##아이디 댓글 가져오기
html_source = driver.page_source
soup = BeautifulSoup(html_source, 'lxml')

youtube_user_IDs = soup.select('div#header-author > a > span')
youtube_comments = soup.select('yt-formatted-string#content-text')


#데이터 정리 함수
def get_str(str_tmp):
    str_tmp = str_tmp.replace("\n", " ")
    str_tmp = str_tmp.replace("\t", " ")
    str_tmp = str_tmp.replace("                ", " ")
    str_tmp = str_tmp.strip()
    return str_tmp


str_userIDs = []
str_comments = []


for i in range(len(youtube_comments)):
    str_comments.append(get_str(str(youtube_comments[i].text)))
    #str_userIDs.append(get_str(str(youtube_user_IDs[i].text)))

youtube_title = "재중동포 유튜브"


file_ = open(f"{youtube_title}_comments.csv", "w", encoding="utf-8", newline="")
wr = csv.writer(file_)

num = 1
wr.writerow(["NUM", "ID", "COMMENT"])

for i in range(len(str_comments)):
    wr.writerow([num, str_comments[i]])
    # wr.writerow([num, str_userIDs[i], str_comments[i]])
    num += 1

file_.close()
driver.close()


#데이터프레임으로 저장 시 활용
#save_folder = "C:/Download"
#df = pd.DataFrame({'댓글 작성자' : str_youtube_userIDs, '댓글' : str_youtube_comments})
#df.index = df.index+1
#df.to_csv('C:/Download/크롤링1.csv', index=False, encoding='utf-8-sig')
#print('save done')`

#ID의 경우 index range 오류로 인해 구동되지 않았음. 필요시 보완 필요
#line 9, 10에 환경에 맞는 드라이버 위치, url 입력
#line 76에 제목 함수 보완하면 좋을 듯