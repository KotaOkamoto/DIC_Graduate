# -*- coding: utf-8 -*-
# 関数をまとめる

# ライブラリのインポート
from ftplib import FTP
import requests
from requests.exceptions import Timeout
import sys
import retry
import time
import datetime
from datetime import datetime as dt
# import lxml.html
# import time
from bs4 import BeautifulSoup
import codecs
import zenhan
from bs4.element import NavigableString, Tag
import random
import pandas as pd
import lxml
import json
import os
from fake_useragent import UserAgent
import re
import pickle
from decimal import Decimal, ROUND_HALF_UP


# 四捨五入する関数
def decimal_half_up(num):
    return Decimal(num).quantize(Decimal("0"), rounding=ROUND_HALF_UP)


# dataonlineの店舗一覧ページから店舗URLを取得する関数
def hall_url_get(soup, header, proxy, hall_list=[], cnt=0, page=1):
    if "データ公開中" in soup.text:
        print("データ公開店舗あり")
        for table in soup.find_all("table", class_="tablesorter"):
            for a in table.find_all("a", class_="clear-box button_border_opened"):
                #print(a.attrs['href'])
                hall_list.append("https://daidata.goraggio.com/" + a.attrs['href'])
                cnt += 1
        print("当該ページ取得完了")
        print("ここまでの総URL取得店舗数:{}".format(cnt))
        countdown_timer(0, 5)
        page += 1
        next_page = "https://daidata.goraggio.com/store_list?pref=&word=&page=" + str(page)
        soup = soup_get_func_retry(next_page, header=header, proxy=proxy)
        countdown_timer(0, 5)
        hall_url_get(soup, header, proxy, hall_list, cnt, page)

    else:
        print("当該ページにデータ公開店舗なし。次の処理に移行。")

    return hall_list


# BeautifulSoupを取得する関数、リトライ5回付き
def soup_get_func_retry(url, header, proxy):
    MAX_RETRY = 5
    stand_by_sec = random.randint(5, 10)
    for i in range(1, MAX_RETRY + 1):
        # 実行したい処理
        try:
            result = requests.get(url, headers=header, proxies=proxy, timeout=(5.0, 7.5))
        # タイムアウト時の処理
        except Timeout:
            print(f"\rタイムアウトしました...\n再接続待機中...{stand_by_sec}秒後に再実行します", end="", flush=True)
            countdown_timer(5, 10)
        # 失敗時の処理
        except Exception as e:
            print(e)
            print("Failed!. retry={}/{}".format(i, MAX_RETRY))
            countdown_timer(5, 10)

        # 失敗しなかった時はループを抜ける
        else:
            print("Success!")
            return BeautifulSoup(result.content, 'html.parser')


# 有料プロキシを運用する関数
# 個人情報なので諸々消してます
def get_proxy():
    proxy_list = ['', '', '', '', '']
    proxy_port = ''
    proxy_username = ''
    proxy_password = ''

    random_proxy = 'http://' + proxy_username + ':' + proxy_password + '@' + random.choice(
        proxy_list) + ':' + proxy_port
    proxy_set = {'http': random_proxy, 'https': random_proxy}

    return proxy_set


# ユーザーエージェントをランダムで取得する関数
def ua_and_proxy_set_func():
    ua = UserAgent()
    header = {"User-Agent": ua.random}
    proxy = get_proxy()
    return header, proxy


# スリープを行う関数
def countdown_timer(min, max):
    t = random.randint(min, max)
    print("wait...")
    for num in reversed(range(t)):
        sys.stdout.write("\rtime wait : {} sec".format(num))
        sys.stdout.flush()
        time.sleep(1)
    print("\ngo to next process...")


# ディレクトリの存在チェック、無ければ生成する
def directory(path, name):
    if os.path.isdir(path):
        print("保存先ディレクトリが存在します。取得済みです。次の処理に移行します。")
        return False
    else:
        print("保存先ディレクトリが存在しません、作成します")
        os.makedirs(path)
        print("ディレクトリ作成完了")
        print("作成ディレクトリ：")
        print(name)

        # 存在チェック
        if os.path.isdir(path):
            print("保存先ディレクトリチェックOK。次の処理へ進みます。")
            return True
        else:
            print("保存先ディレクトリチェックNG。処理を終了します。ディレクトリを確認してください。")
            exit(0)


# 今日から14日前までの日付分の文字列リストを生成する関数
# yyyy-mm-dd形式
def fourteendays(max=15):
    past_date = []
    for i in range(1, max):
        day = datetime.date.today() + datetime.timedelta(days=-i)
        past_date.append(day.strftime("%Y/%m/%d").replace("/", "-"))
    return past_date

# 今日から20日前までの日付分の文字列リストを生成する関数
# yyyy-mm-dd形式
def twentydays(max=21):
    past_date = []
    for i in range(2, max):
        day = datetime.date.today() + datetime.timedelta(days=-i)
        past_date.append(day.strftime("%Y/%m/%d").replace("/", "-"))
    return past_date


# 台ごとのhtmlを取得する関数
def unit_html_get(unit_url_list, soup, date, header, proxy, store_path, hall_id):
    if unit_url_list == []:
        # table取ってURL取ってdate指定して取得
        for table in soup.find_all("table", class_="sorter tablesorter"):
            for unit_url in table.find_all("a", class_="Text-UnderLine"):
                target_url = unit_url.attrs['href'] + "&target_date=" + date
                print(target_url)
                unit_url_list.append(unit_url.attrs['href'])
                f_name = "unit_" + unit_url.text
                #print("check before soup")
                soup = soup_get_func_retry(target_url, header, proxy)
                #print("check soup over")
                with codecs.open(store_path + "\\" + f_name + ".html", 'w', 'utf_8') as f:
                    f.write(soup.prettify())
                countdown_timer(0, 3)
    else:
        for unit_url in unit_url_list:
            target_url = unit_url + "&target_date=" + date
            print(target_url)
            unit_num = unit_url.replace("https://daidata.goraggio.com/" + hall_id + "/detail?unit=", "").replace(
                "&target_date=" + date, "")
            f_name = "unit_" + unit_num
            #print("check before soup")
            soup = soup_get_func_retry(target_url, header, proxy)
            #print("check soup over")
            with codecs.open(store_path + "\\" + f_name + ".html", 'w', 'utf_8') as f:
                f.write(soup.prettify())
            countdown_timer(0, 3)


# 指定パス内のデータをリストアップする関数
def file_count_func(path):
    file_list = []
    for file in os.listdir(path):
        file_list.append(file)
    return file_list


# 指定パス内のディレクトリのみをリストアップする関数
def dir_listup_func(path):
    dir_list = []
    for dir in os.listdir(path):
        dir = path + "\\" + dir
        if os.path.isdir(dir):
            dir_list.append(dir)
    return dir_list


# 上手く取得できなかったhtmlを再取得する関数
def re_get_html(diff_dict, hall_id, path, unit_num_master):
    num_pattern = r"\d+"
    if len(diff_dict) == 0:
        return
    for diff in diff_dict.items():
        date = diff[0]
        count = diff[1]
        dir_path = path + "\\" + date
        #print(dir_path)
        file_list = file_count_func(dir_path)
        num_list = []
        for line in file_list:
            match = re.search(num_pattern, str(line))
            num_list.append(int(match.group()))
        # print(num_list)
        # print(len(num_list))
        not_list = list(set(unit_num_master) - set(num_list))
        # print(not_list)
        print("hall_id : {} \n date : {} \n 未取得数 : {}".format(hall_id, date, len(not_list)))

        header, proxy = ua_and_proxy_set_func()
        print("header:{},proxy:{}".format(header, proxy))

        for unit_num in not_list:
            target_url = "https://daidata.goraggio.com/" + hall_id + "/detail?unit=" + str(
                unit_num) + "&target_date=" + date
            print(target_url)
            f_name = "unit_" + str(unit_num)
            # print("check before soup")
            soup = soup_get_func_retry(target_url, header, proxy)
            # print("check soup over")
            with codecs.open(dir_path + "\\" + f_name + ".html", 'w', 'utf_8') as f:
                f.write(soup.prettify())
            countdown_timer(0, 3)


# url listをファイルから取得する関数
def url_file_to_list(file_path, pattern):
    available_url_list = []
    with codecs.open(file_path, "r", "utf-8") as f:
        for line in f:
            if not line:
                print("!!ERROR!! not found url list")
                print("now in the [url_file_to_list] function")
                exit(0)
            elif re.search(pattern, line):
                match = re.search(pattern, line)
                unacq_url = match.group()
                # print(str(count)+":"+hold_url)
                available_url_list.append(unacq_url)  # 差分URLリストを作成
    return available_url_list


# ステータスファイルの存在チェック
def status_file_check(path):
    if os.path.isfile(path):
        return True
    else:
        return False


# パスとデータを指定すると上書きモードで保存してくれる関数
def store_file(file, data):
    with open(file, mode="w", encoding="utf-8") as f:
        for line in data:
            # print(line)
            f.write("{}\n".format(line))


# pickleを保存する関数
def store_pickle(name, data):
    with open(str(name) + ".pickle", "wb") as f:
        pickle.dump(data, f)

# pickleを読み込む関数
def load_pickle(name):
    with open(str(name) + '.pickle', 'rb') as f:
        data_name = pickle.load(f)
    return data_name

# pickleの存在チェック
def pickle_check(path):
    if os.path.isfile(path):
        return True
    else:
        return False

# pickle保存ディレクトリの存在チェック
def pickle_dir_check(path):
    if os.path.isdir(path):
        return True
    else:
        return False
