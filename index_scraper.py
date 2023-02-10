import datetime
import time
import re
import csv
import numpy as np
import pandas as pd
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
import tqdm
import os
import concurrent.futures

# ID = '202205050307'
# ID_for_URL = ID[2:]
# URL = f'http://jiro8.sakura.ne.jp/index.php?code={ID_for_URL}'
FOLDER = 'data'
FILE = 'index.csv'
INDEX_X_PATH = '/html/body/table[3]/tbody/tr/td[3]/table[3]/tbody/tr[{NUM}]'
INDEX_X_PATHS = [INDEX_X_PATH.format(NUM = num) for num in [33, 34, 35, 36, 49, 50, 51, 52, 65, 66, 67, 68, 81, 82, 83, 84, 97, 98, 99, 100]]
RETURN_DF_COLS = ['lead_index_1','pase_index_1','up_index_1','speed_index_1'
           ,'lead_index_2','pase_index_2','up_index_2','speed_index_2'
           ,'lead_index_3','pase_index_3','up_index_3','speed_index_3'
           ,'lead_index_4','pase_index_4','up_index_4','speed_index_4'
           ,'lead_index_5','pase_index_5','up_index_5','speed_index_5']

def create_folder():
    if not os.path.exists(FOLDER):
        os.mkdir(FOLDER)

def is_file_exists():
    return os.path.exists(f'{FOLDER}/{FILE}')

def get_latest_record():
    df = pd.read_csv(f'{FOLDER}/{FILE}')
    return max(df.race_id)

def split_list(l, n):
    """
    リストをサブリストに分割する
    :param l: リスト
    :param n: サブリストの要素数
    :return: 
    """
    for idx in range(0, len(l), n):
        yield l[idx:idx + n]

def launch_chrome_driver(is_headless = False):
    options = webdriver.ChromeOptions()
    if is_headless:
        options.add_argument('--headless')
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    return driver

def clean_data(data:str) -> list:
    data_list = data.split(' ')
    return data_list

def delete_extra_str(hourse_number):
    return hourse_number[:-1]

def get_horse_number(driver):
    raw_data = driver.find_element_by_xpath('/html/body/table[3]/tbody/tr/td[3]/table[3]/tbody/tr[2]').text
    data_list =  clean_data(raw_data)
    data_list = delete_extra_str(data_list)
    return data_list

def get_index_list(driver, horse_number):
    index_list = []
    for path in INDEX_X_PATHS:
        for i in range(1, len(horse_number) + 1):
            driver = driver.find_element_by_xpath(path + '/td[{num}]'.format(num = i))
            index_list.append(driver.text)
    return index_list

def convert_list_to_df(index_list, horse_number):
    return pd.DataFrame(np.array(index_list).reshape(int(len(index_list)/len(horse_number)), len(horse_number)))
    
def add_columns(df):
    df.columns = RETURN_DF_COLS
    return df

def get_index_df(id:str):
    id_for_url = id[2:]
    url = f'http://jiro8.sakura.ne.jp/index.php?code={id_for_url}'
    Chrome = launch_chrome_driver(True)
    Chrome.get(url)
    horse_number = get_horse_number(Chrome)
    indexs = get_index_list(Chrome, horse_number)
    Chrome.close()
    index_df = convert_list_to_df(indexs, horse_number)
    df = index_df.T
    df = add_columns(df)
    df['race_id'] = id
    return df

def create_race_id_list(latest_id =None):
    seireki_list = [str(s) for s in list(range(2010, 2024))]
    # 01：札幌、02：函館、03：福島、04：新潟、05：東京、06：中山、07：中京、08：京都、09：阪神、10：小倉
    spot_list = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10']
    num_list = ['01', '02', '03', '04', '05', '06', '07']
    date_list = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14']
    race_list = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    id_list = []
    for seireki in seireki_list:
        for spot in spot_list:
            for num in num_list:
                for date in date_list:
                    for race in race_list:
                        id_list.append(seireki + spot + num + date + race)
    if latest_id:
        id_list = id_list[id_list.index(latest_id)+1:]
    return id_list

def main():
    create_folder()
    if is_file_exists():
        latest_id = str(get_latest_record())
        id_list = create_race_id_list(latest_id)
    else:
        id_list = create_race_id_list()
    id_lists = list(split_list(id_list, 10))
    all_df = pd.DataFrame(columns = RETURN_DF_COLS)
    faild_list = []
    for id_list in tqdm.tqdm(id_lists):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = [executor.submit(get_index_df, id) for id in id_list]
            for result, id in zip(results, id_list):
                try:
                    all_df = all_df.append(result.result())
                except NoSuchElementException:
                    faild_list.append(id)
                    continue
                except KeyboardInterrupt:
                    all_df.to_csv('index.csv')
                    break
                time.sleep(5)
    all_df.to_csv(f'{FOLDER}/{FILE}', index = False)
    with open(f'{FOLDER}/failedlist.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        for row in faild_list:
            writer.writerow(row)
if __name__ == '__main__':
    main()