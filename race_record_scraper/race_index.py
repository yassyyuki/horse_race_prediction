import numpy as np
import pandas as pd
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

KEIBASHINBUN_URL = 'http://jiro8.sakura.ne.jp/index.php?code={ID}'

def launch_chrome_driver(is_headless = False):
    options = webdriver.ChromeOptions()
    if is_headless:
        options.add_argument('--headless')
    options.add_argument("--no-sandbox")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    return driver

def get_race_index(driver):
    horse_number = driver.find_element_by_xpath('/html/body/table[3]/tbody/tr/td[3]/table[3]/tbody/tr[2]').text
    lead_index = driver.find_element_by_xpath('/html/body/table[3]/tbody/tr/td[3]/table[3]/tbody/tr[14]').text
    pase_index = driver.find_element_by_xpath('/html/body/table[3]/tbody/tr/td[3]/table[3]/tbody/tr[15]').text
    up_index = driver.find_element_by_xpath('/html/body/table[3]/tbody/tr/td[3]/table[3]/tbody/tr[16]').text
    speed_index = driver.find_element_by_xpath('/html/body/table[3]/tbody/tr/td[3]/table[3]/tbody/tr[17]').text
    return horse_number, lead_index, pase_index, up_index, speed_index

def clean_data(data:str) -> list:
    data_list = data.split(' ')
    return data_list
    
def delete_extra_str(hourse_number):
    return hourse_number[:-1]

def get_race_index_df(id):
    global KEIBASHINBUN_URL
    url = KEIBASHINBUN_URL.format(ID = id[2:])
    Chrome = launch_chrome_driver(True)
    Chrome.get(url)
    horse_number, lead_index, pase_index, up_index, speed_index = get_race_index(Chrome)
    horse_number = clean_data(horse_number)
    horse_number = delete_extra_str(horse_number)
    lead_index = clean_data(lead_index)
    pase_index = clean_data(pase_index)
    up_index = clean_data(up_index)
    speed_index = clean_data(speed_index)
    df = pd.DataFrame(np.array([horse_number, lead_index, pase_index, up_index, speed_index]).T,
                    columns = ['hourse_number', 'lead_index', 'pase_index', 'up_index', 'speed_index'])
    df['race_id'] = id
    Chrome.close()
    return df