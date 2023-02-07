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

def separate_course_info(course_info):
#ハードコーディングになっちゃった
    road_type = course_info[0]
    curve_info = course_info[1]
    course_length = course_info[2:course_info.find('m')]
    weather = course_info[course_info.find('天候')+5]
    road_situation = course_info[course_info.rfind(road_type)+6]
    time = course_info[course_info.find('発走')+5:]
    return road_type, curve_info, course_length, weather, road_situation, time

def get_race_record_df(id):
    global NETKEIBA_URL
    url = NETKEIBA_URL.format(ID = id)
    target_html = requests.get(url).content
    soup = BeautifulSoup(target_html, 'html.parser')
    elements = get_elements_around_tabel(soup)
    texts = get_texts_from_elements(elements)
    df = reshape_texts_to_df(texts)

    course_info = get_course_info(soup)
    road_type, curve_info, course_length, weather, road_situation, time = separate_course_info(course_info)

    df['road_type'] = road_type
    df['curve_info'] = curve_info
    df['course_length'] = course_length
    df['weather'] = weather
    df['road_situation'] = road_situation
    df['time'] = time
    df['race_id'] = id
    return df