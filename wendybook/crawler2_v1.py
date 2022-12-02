import os, time, multiprocessing, itertools
from pickletools import read_uint1
import pandas as pd
from sys import platform


from D2_ARlevel import per_level as PER_LEVEL
from D1_book import driver as driver # call chrome webdriver in this file 


def Level_crawler(Lv,
                  end_page_num,
                  SAVE_PATH):
    print(f'Lv{Lv} start crawling')
    df_lv = pd.DataFrame()
    #### Low Performance: 1 it/s ####
    for pg in range(1, end_page_num+1):
        df_temp = PER_LEVEL(level=Lv, page=pg)
        
        df_lv = pd.concat([df_lv, df_temp], axis=0)
        print(f'Level: {Lv}, Page: {pg}/{end_page_num}')
        time.sleep(60)
    
    #### Multiprocessing ####
    # pool = multiprocessing.Pool(4) # using 4 CPU
    
    # if __name__ == '__main__': # to protect program
    #     multiprocessing.freeze_support()
    #     page_length = range(1, end_page_num+1)
    #     result = pool.starmap(PER_LEVEL, 
    #                         zip(itertools.repeat(Lv, 
    #                                             len(page_length)), 
    #                             page_length
    #                             )
    #                         )
    #     print(type(result))
    #     df_lv = pd.concat([df_lv, result], axis = 0)




    tot_SAVE_PATH = os.path.join(os.getcwd(), SAVE_PATH, f'wendybook_Lv{Lv}.xlsx')
    df_lv.to_excel(tot_SAVE_PATH)
    return df_lv


# df_lv1 = Level_crawler(Lv=1, end_page_num=1, SAVE_PATH='RESULT')
# df_lv2 = Level_crawler(Lv=2, end_page_num=5, SAVE_PATH='RESULT')
# df_lv3 = Level_crawler(Lv=3, end_page_num=9, SAVE_PATH='RESULT')
# df_lv4 = Level_crawler(Lv=4, end_page_num=11, SAVE_PATH='RESULT')
# time.sleep(600)
# df_lv5 = Level_crawler(Lv=5, end_page_num=9, SAVE_PATH='RESULT')
# time.sleep(400)
# df_lv6 = Level_crawler(Lv=6, end_page_num=7, SAVE_PATH='RESULT')
df_lv7 = Level_crawler(Lv=7, end_page_num=2, SAVE_PATH='RESULT')
df_lv8 = Level_crawler(Lv=8, end_page_num=1, SAVE_PATH='RESULT')
df_lv9 = Level_crawler(Lv=9, end_page_num=1, SAVE_PATH='RESULT')