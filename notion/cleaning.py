from glob import glob
import os
import re
import pickle
import unicodedata
from tqdm import tqdm

BASE_DIR = os.getcwd()

def Loader(file_name):
    global BASE_DIR
    pkl_obj = open(os.path.join(BASE_DIR, 'RESULT', file_name), 'rb')
    crawling_result = pickle.load(pkl_obj)

    return crawling_result

def default(crawling_result): # crawled result
    result = {}

    def xad_cleaner(inputText):
        print('>> before: ', inputText)
        output = re.sub(u'\xad', u' ', inputText)
        output = re.sub(r'\n', '', output)
        output = re.sub(' ', '', output)
        # output = unicodedata.normalize("NFKD", output)
        
        # print('>> after: ', output)
        return output

    print('>> cleaning initate with : ', len(crawling_result))
    for idx, page in tqdm(enumerate(crawling_result), desc='>> cleaning each page'):
        # 사람, 내용이 비어있으면 버리는 것으로 결정
        if ('people' not in page.keys()) or ('content' not in page.keys()):
            continue
        else:
            cont1 = re.sub(r'\n', ' ', page['content'])
            cont2 = re.sub(
                '[^a-zA-Z0-9ㄱ-ㅣ가-힣 ~`\.\,!@#$%^&*\(\)\[\]{}\-\_\'\"><\/\?=+:;]', '', cont1)
            page['content'] = cont2
            newKey = xad_cleaner(page['people'])
            page.pop('people')
            result[newKey] = page

    print('>> cleaning finished with : ', len(result.keys()))

    return result


if __name__ == '__main__':

    data = Loader(file_name='220227_2021 STELA 발제내용.pkl')
    rs = default(crawling_result=data)
