import os
import sys
import re
import argparse
import warnings
import collections
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

# argument
parser = argparse.ArgumentParser(description='validate')
parser.add_argument('--solution', action='store_true',
                    help="solution")
parser.add_argument('--channel', action='store_true',
                    help="channel talk")

# args = parser.parse_args('') #!# in jupytor notebook case
args = parser.parse_args()

class Validator:
    def __init__(self, file_name):
        self.df = pd.read_excel(os.path.join(Project_PATH, 'jobkorea', 'result', file_name))
        self.col_task2 = '사용솔루션'
        self.col_task3 = '채널톡사용여부'

    def task2(self, allowed_string):
        r"""validation of string
        allowed_string: list
            list of allowed string
        """
        unique_val = collections.Counter(self.df[self.col_task2].unique()).keys()
        if unique_val == allowed_string:
            return None
        else:
            raise ValueError('>> something wrong, check values: ', unique_val)
        
    def task1(self):
        r"""Validation of jobkorea crawling
        """
        df_error = self.df[self.df['매출수'] == 'error']
        print('>> error: ', df_error.shape[0])

        return self.df #!# 단순히 다시 토함
        


if __name__ == '__main__':
    validator = Validator('task2_3.xlsx')
    
    if args.solution:
        validator.task2(['N', 'Y'])
    
    elif args.channel:
        pass