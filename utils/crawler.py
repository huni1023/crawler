from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, WebDriverException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver

import os, sys, time
import re
import copy
import argparse
import warnings
import math
import platform
import logging 
import pandas as pd
from tqdm import tqdm
warnings.filterwarnings('ignore')

#now we will Create and configure logger 
logging.basicConfig(filename="std.log", 
					format='%(asctime)s %(message)s', 
					filemode='w')
logger = logging.getLogger()
logger.setLevel(logging.ERROR) # error level logging
logger.propagate = False # options for no output logs to console


# set utils
util_path = os.pardir
if util_path not in sys.path:
    sys.path.append(os.pardir)
from utils.helper import load_config


Project_PATH = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
Save_PATH = os.path.join(Project_PATH, 'jobkorea', 'result')

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

class Cralwer:
    def __init__(self, selenium_path, chrome_option):
        r"""
        Parameters
        ----------
        selenium_path: string
        chrome_option: webdriver parmaters
        """
        self.driver = webdriver.Chrome(
            executable_path = selenium_path, chrome_options=chrome_option
        )
        self.ACC = ActionChains(self.driver)
        