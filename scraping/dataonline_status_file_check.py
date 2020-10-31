# -*- coding: utf-8 -*-
# status.jsonの存在チェック及びなければ新規生成するプログラム

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
url_pattern = r"https://daidata.goraggio.com//[0-9]+"


def url_file_to_list(file_path):
    available_url_list = []
    with codecs.open(file_path, "r", "utf-8") as f:
        for line in f:
            if not line:
                print("!!ERROR!! not found url list")
                print("now in the [url_file_to_list] function")
                exit(0)
            elif re.search(url_pattern, line):
                match = re.search(url_pattern, line)
                unacq_url = match.group()
                # print(str(count)+":"+hold_url)
                available_url_list.append(unacq_url)  # 差分URLリストを作成
    return available_url_list


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


# 最新の取得可能店舗リスト読み込み
#path = "D:\\myVSCodeProg\\AI\\test\\dataonline\\now_available_stores.txt"

# ひとまず東京分のみ
path = "./dataonline/hall_list.txt"

url_list = url_file_to_list(path)
#print(url_list[0])
#exit(0)


# status.jsonが無ければ生成する
for line in url_list:
    #print(line)
    hall_id = line.replace("https://daidata.goraggio.com//", "")
    #print(hall_id)
    f_path = "./dataonline/html/" + hall_id + "/status.json"
    print(f_path)

    if status_file_check(f_path):
        print("jsonあり。次の店舗へ。")
        pass
    else:
        print("jsonなし、htmlからjsonを作成します。")
        store_dict = {}
        header, proxy = ua_and_proxy_set_func()
        print("header:{},proxy:{}".format(header, proxy))
        soup = soup_get_func_retry(line, header, proxy)
        for title in soup.find_all("title"):
            hall_name = title.text.replace(" - 台データオンライン","").strip()
            print(hall_name)
            store_dict["hall_ID"] = hall_id
            store_dict["hall_name"] = hall_name
        for h2p in soup.find_all("h2", class_="pachinko"):
            p = h2p.text.replace("Pachinkoパチンコ | ", "").replace("台","")
            print(p)
            store_dict["p_units"] = int(p)
        for h2s in soup.find_all("h2", class_="slot"):
            s = h2s.text.replace("Slotスロット | ", "").replace("台","")
            print(s)
            store_dict["s_units"] = int(s)
        for ul in soup.find_all("ul", class_="pachinko"):
            for a in ul.find_all("a"):
                if "台番号で探す" in a.text:
                    p_all_url = a.attrs["href"]
                    store_dict["p_unit_num"] = unit_num_get(p_all_url)
        for ul in soup.find_all("ul", class_="slot"):
            for a in ul.find_all("a"):
                if "台番号で探す" in a.text:
                    s_all_url = a.attrs["href"]
                    store_dict["s_unit_num"] = unit_num_get(s_all_url)
        print(store_dict)

        with codecs.open(f_path, 'w', 'utf-8') as f:
            json.dump(store_dict, f, ensure_ascii=False, indent=4)

        countdown_timer(5, 10)


print("FINISH!!")

