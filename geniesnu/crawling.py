import os
import sys
import platform
from pathlib import Path
from selenium import webdriver

# set utils
util_path = os.pardir
if util_path not in sys.path:
    sys.path.append(os.pardir)


from utils.crawler import Cralwer
from utils.telegram_bot import TelegramBot 
from utils.helper import load_config

Project_PATH = Path(__file__).parent.absolute().parent.absolute()
print('project path', Project_PATH)
Save_PATH = os.path.join(Project_PATH, 'geniuesnu', 'result')


# load config file : 수정되어야 함
CONFIG_PATH = "config.yaml"
config = load_config(os.path.join(Project_PATH, 'utils', CONFIG_PATH))
selen_path_dict = config['selen_path']
chrome_opt_dict = config['chrome_option']

# chrome option
chrome_opt = webdriver.ChromeOptions()
for _ in chrome_opt_dict['default']:
    chrome_opt.add_argument(_)
# chrome_opt.add_experimental_option("detach", True) # prevent automatically closed tab
# chrome_opt.add_experimental_option("excludeSwitches", ["enable-logging"])

if platform.system() == 'Linux':
    for _ in chrome_opt_dict['headless']:
        chrome_opt.add_argument(_)
    chrome_opt.add_argument(f'user-agent={chrome_opt_dict["user_agent"]}')


class snugenie_crawler(Cralwer):
    global config
    def __init__(self, url):
        if platform.system() == 'Linux':
            print('itis: ', config['selen_path']['ubuntu2'])
            super().__init__(selenium_path=config['selen_path']['ubuntu2'],
                            chrome_option=chrome_opt)
        else:
            raise NotImplementedError
        self.url = url
        
        # test
        self.driver.get(self.url)
        print('current url: ', self.driver.current_url)
        

if __name__ == '__main__':
    crawler = snugenie_crawler(url='https://naver.com')
    