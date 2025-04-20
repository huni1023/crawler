from argparse import Action
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver import ActionChains
from selenium import webdriver
import os
import copy
import time
import datetime
import pickle
import warnings
from sys import platform
from tqdm import tqdm


warnings.filterwarnings('ignore')
chrome_opt = webdriver.ChromeOptions()



class Load:
    def __init__(self, USER, image=False):
        '''
        1. USER(str): verifying user name
        2. image(boolean): on/off image option 
        '''
        print('Current OS : ', platform)
        print('Current OS username: ', os.getlogin())

        if USER == 'huni1023':
            if 'darwin' in platform:
                seleniumPath = '/Users/huni/Dropbox/내 Mac (MacBook-Pro.local)/Downloads/chromedriver'
                if image: pass
                else: 
                    chrome_opt.add_argument('--kiosk')

            elif 'win32' in platform:
                if image: pass
                else: 
                    prefs = {"profile.managed_default_content_settings.images": 2}
                    chrome_opt.add_experimental_option("prefs", prefs)
                    
                chrome_opt.add_experimental_option("excludeSwitches", ["enable-logging"]) # shut down error msg
                chrome_opt.add_argument('--start-maximized')

                if os.getlogin() == 'jhun1':
                    seleniumPath = r'C:\Users\jhun1\Dropbox\My PC (LAPTOP-VLNR6K8R)\Downloads\chromedriver_win32\chromedriver'
                elif os.getlogin() == 'snukh':
                    seleniumPath = r'C:\Users\snukh\Downloads\chromedriver_win32\chromedriver'
                else:
                    raise ValueError('Define driver path in this device')
        else:
            raise ValueError('Set User name and exrtra argument')
            

        self.driver = webdriver.Chrome(executable_path=seleniumPath, chrome_options=chrome_opt)
        self.actionChain = ActionChains(self.driver)
        self.BASE_DIR = os.getcwd()
        
class Crawler(Load):
    def __init__(self, USER, targetUrl # 크롤링할 링크
                ):
        super().__init__(USER)
        self.targetUrl = targetUrl

    def D1(self, test_opt=False):
        print('\n\n>>>> Crawling Previous Presentation in Table')
        self.driver.get(self.targetUrl)
        time.sleep(3)
        Table = self.driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div[1]/div[2]/div/div[5]')
        outputLS = []

        # crawler
        # 한줄 한줄 마우스 올려서 href 확인하기
        # 날짜, 제목, 링크, 발제자
        # Table = self.driver.find_element_by_class_name('notino-table-view')
        if test_opt == True:
            print(type(Table))

        BlockLs = Table.find_elements_by_class_name('notion-collection-item')
        print('>>> Length: ', len(BlockLs))
        for each_block in tqdm(BlockLs, desc='>> crawling each page meta info..'):
            temp = {}

            title_block = each_block.find_element_by_css_selector('div:nth-child(5) > div:nth-child(1)')
            title = title_block.text
            temp['title'] = title
            print('>> right: ', title)
            day = each_block.find_element_by_css_selector('div:nth-child(1)').text
            temp['day'] = day
            people = each_block.find_element_by_css_selector(
                'div:nth-child(6)').text
            temp['people'] = people

            self.actionChain.move_to_element(title_block).perform()
            # if 'darwin' in platform: 
                # (80, -30/-29)하면 열리는 것: 3줄짜리
                # (80. -28)하면 열리는 것
                # 1번 idx에서 성공함 # .move_by_offset(80, -30).perform() # positive direction: right, bottom
                # .move_by_offset(80, -29) 
                # delay = 5
                # overlay = WebDriverWait(self.driver, delay).until(EC.presence_of_element_located((By.CLASS_NAME, 'notion-peek-renderer')))
                # open_as_page = overlay.find_element_by_css_selector('a') 
                # link = open_as_page.get_attribute('href')
                # except StaleElementReferenceException:
                #     .move_by_offset(80, -25)

            # else: print('setting')
            time.sleep(1)
            Table_re = self.driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div[1]/div[2]/div/div[5]')
            a_blocks = Table_re.find_elements_by_css_selector('a')
            for block in a_blocks:
                link = block.get_attribute('href')
                if 'youtube' in link: continue
                elif 'dndrl' in link:
                    temp['link'] = link
                    break
            
            outputLS.append(temp)
            

        self.driver.close()
        return outputLS


    def D2(self,
        RS1,  # D1 결과
        save_folder, # 파일 저장 위치
        test_opt = False, # 테스트 할 때
            ):
        df = copy.deepcopy(RS1)
        
        # 페이지 진입
        for idx, page in tqdm(enumerate(RS1), desc = '>> crawling each page'):
            assert type(page) == dict, print(page)
            try:
                self.driver.get(page['link']) ; time.sleep(3)
            except KeyError:
                print(f'>>> passing : ', idx)
                continue
            # 텍스트 모두 드러나게 클릭하는 작업

            Content = self.driver.find_element_by_class_name('notion-page-content').text
            df[idx]['content'] = Content
        
        if test_opt == True:
            print('>>>> Sample', df[0])


        today = str(datetime.datetime.now()).replace('-', '')[2:8]
        file_name = today+'_2021 STELA 발제내용' + '.pkl'
        save_dir = os.path.join(self.BASE_DIR, save_folder, file_name)
        with open(save_dir, 'wb') as outp:
            pickle.dump(df, outp)

        pass


if __name__ == '__main__':
    # baseSetup = Load(USER='huni1023')

    crawler = Crawler(USER='huni1023', targetUrl='https://dndrl.notion.site/28b270dfd58d497cbd031f457f02ed92?v=c081bcadc88a486683c7e7325ea99174')
    rs1 = crawler.D1()
    # print(rs1[0])

    rs2 = D2(RS1 = rs1, 
            save_folder = 'RESULT',
            test_opt= True,
            )

