# -*- coding: utf-8 -*-
# ディレクトリとファイル構成の整合性を確認するプログラム

# ライブラリのインポート
import os
import re

import requests
from requests.exceptions import Timeout
import time
from bs4 import BeautifulSoup
import codecs
import random
from fake_useragent import UserAgent
import json
from config import *

# 正規表現コンパイル
url_pattern = r"https://daidata.goraggio.com/[0-9]+"
num_pattern = r"\d+"



def status_file_check(path):
    if os.path.isfile(path):
        return True
    else:
        return False


def unit_num_get(url):
    df = pd.read_html(url)
    series = df[0].iloc[:, 1]
    unit_num = series.values.tolist()
    return unit_num


def file_count_func(path):
    file_list = []
    for file in os.listdir(path):
        file_list.append(file)
    return file_list


def file_count_twentydays(path, units):
    file_count = {}
    past_date = twentydays()
    for date in past_date:
        date_dir = path + "\\" + date
        files = os.listdir(date_dir)
        if "data.csv" in files and "data.zip" in files:
            print("directory is over!!")
            file_count[date] = units
        else:
            count = len(files)
            file_count[date] = count
    return file_count


def diff_file_count(units, file_count):
    diff_list = {}
    for date, count in file_count.items():
        if units == count:
            pass
        else:
            print("difference!")
            print("unit : {} date : {} count : {}".format(units, date, count))
            diff_list[date] = int(units) - int(count)
    return diff_list




# 最新の取得可能店舗リスト読み込み
#path = "D:\\myVSCodeProg\\AI\\test\\dataonline\\now_available_stores.txt"

# ひとまず東京分のみ
path = "./hall_list.txt"

url_list = url_file_to_list(path, url_pattern)
#print(url_list[0])
#exit(0)

# 一店舗分のみ回す用
# url_list = ["https://daidata.goraggio.com/100260"]


for line in url_list:
    print(line)
    hall_id = line.replace("https://daidata.goraggio.com/", "")
    print(hall_id)
    cur_path = "./dataonline/html/" + hall_id
    p_path = cur_path + "/p"
    s_path = cur_path + "/s"
    f_path = cur_path + "/status.json"
    print(f_path)

    if status_file_check(f_path):
        print("jsonあり。チェック開始。")
        with codecs.open(f_path, "r", "utf-8") as f:
            status = json.load(f)
        #print(status)
        if "p_units" in status:
            print("pachinko check")
            p_units = status["p_units"]
            p_unit_num_master = status["p_unit_num"]
            p_file_count = file_count_twentydays(p_path, p_units)
            print(p_file_count)
            p_diff_dict = diff_file_count(p_units, p_file_count)
            if len(p_diff_dict) == 0:
                print("pachi : {}".format(p_diff_dict))
                print("No diff, move to the slot dir")
            else:
                print("pachi : {}".format(p_diff_dict))
                print("未取得分を取得開始")
                re_get_html(p_diff_dict, hall_id, p_path, p_unit_num_master)
                print("over!! move to the slot dir")

        if "s_units" in status:
            print("slot check")
            s_units = status["s_units"]
            s_unit_num_master = status["s_unit_num"]
            s_file_count = file_count_twentydays(s_path, s_units)
            s_diff_dict = diff_file_count(s_units, s_file_count)
            if len(s_diff_dict) == 0:
                print("slot : {}".format(s_diff_dict))
                print("No diff, move to the next hall")
            else:
                print("slot : {}".format(s_diff_dict))
                print("未取得分を取得開始")
                re_get_html(s_diff_dict, hall_id, s_path, s_unit_num_master)
                print("over!! move to the next hall")

    else:
        print("NO json! please run [dataonline_status_file_check.py]!")
        countdown_timer(5, 10)


print("FINISH!!")

