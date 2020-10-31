# -*- coding: utf-8 -*-
# 台データオンラインの取得可能店舗を確認するシステム

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
from datetime import datetime as dt
from config import *

# 正規表現コンパイル
url_pattern = r"https://daidata.goraggio.com//[0-9]+"

today = dt.today()
today_str = today.strftime("%Y/%m/%d").replace("/","_")


diff_path = "./available/pickle/diff.pickle"
pre_path = "./available/pickle/pre.pickle"
now_path = "./available/pickle/now.pickle"

# 最新のデータ -> now_available_stors.txt
# 一個前のデータ -> pre_available_stors.txt
# 差分 -> com_xxxx_xx_xx.txt
# それより前のもの -> pickleで保管

if not pickle_check(diff_path):
    # 前回起動時までの取得可能店舗リスト読み込み
    path = "./now_available_stores.txt"

    pre_available_url_list = []
    count = 0

    f = codecs.open(path, "r", "utf-8")
    for line in f:
        #print(line)
        if not line:
            print("!!ERROR!! not found url list")
            exit(0)
        elif re.search(url_pattern, line):
            match = re.search(url_pattern, line)
            unacq_url = match.group()
            # print(str(count)+":"+hold_url)
            pre_available_url_list.append(unacq_url)  # 差分URLリストを作成
            count += 1
    f.close()

    # print(pre_available_url_list)
    # 今回起動時の取得可能店舗取得
    init_url = "https://daidata.goraggio.com/store_list?pref=&word="
    hall_list = []

    header, proxy = ua_and_proxy_set_func()
    print("header:{},proxy:{}".format(header, proxy))
    soup = soup_get_func_retry(init_url, header, proxy)
    now_available_url_list = hall_url_get(soup, header, proxy, hall_list)
    print("url取得完了。差分チェック開始。")

    diff = list(set(pre_available_url_list) ^ set(now_available_url_list))

    store_pickle(diff_path, diff)
    store_pickle(pre_path, pre_available_url_list)
    store_pickle(now_path, now_available_url_list)

else:
    print("pickle load")
    diff = load_pickle(diff_path)
    pre_available_url_list = load_pickle(pre_path)
    now_available_url_list = load_pickle(now_path)

diff = list(set(pre_available_url_list) ^ set(now_available_url_list))
print("pre_listの件数 : {}".format(len(pre_available_url_list)))
print("now_listの件数 : {}".format(len(now_available_url_list)))

if len(diff) < 1:
    print("差分チェック。差分なし。")
else:
    print("{}件の差分あり。".format(str(len(diff))))
    for i in diff:
        print("差分URL : {}".format(i))


store_file("./available/comp/comp_" + today_str + ".txt", diff)
store_file("./available/pre_available_stores.txt", pre_available_url_list)
store_file("./available/now_available_stores.txt", now_available_url_list)

print("FINISH!!")

