#https://db.netkeiba.com/race/202005020106/
#レース情報のスクレイピング
import pandas as pd
import numpy as np
import requests
from lxml import html
from bs4 import BeautifulSoup

NETKEIBA_URL = 'https://db.netkeiba.com/race/{ID}/'
COURSE_INFO_X_PATH = '/html/body/div[1]/div[2]/div[1]/div/div/div/diary_snap/div/div/dl/dd/p/diary_snap_cut/span'

def get_elements_around_tabel(soup):
    table_html = soup.find('table')
    elements = table_html.find_all(nowrap="nowrap")
    return elements

def get_texts_from_elements(elements):
    texts = [element.text.replace('\n', '') for element in elements]
    return texts

def reshape_texts_to_df(texts):
#上手い書き方求む
    array = np.array(texts).reshape(int(len(texts)/21), 21)
    df = pd.DataFrame(array[1:], columns = array[0])
    return df

def get_course_info(soup):
    lxml = html.fromstring(str(soup))
    course_info_element = lxml.xpath(COURSE_INFO_X_PATH)
    course_info = course_info_element[0].text.replace('\xa0', '')
    return course_info

def get_race_record_df(id):
    global NETKEIBA_URL
    url = NETKEIBA_URL.format(ID = id)
    target_html = requests.get(url).content
    soup = BeautifulSoup(target_html, 'html.parser')
    elements = get_elements_around_tabel(soup)
    texts = get_texts_from_elements(elements)
    df = reshape_texts_to_df(texts)
    df['race_id'] = id
    return df
