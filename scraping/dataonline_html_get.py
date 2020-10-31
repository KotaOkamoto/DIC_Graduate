# -*- coding: utf-8 -*-
#データオンラインのhtmlデータをブッコ抜くシステム

#ライブラリのインポート
from config import *


today = dt.today()
today_str = today.strftime("%Y/%m/%d").replace("/","-")
yesterday = datetime.date.today()+datetime.timedelta(days=-1)
yesterday_str = yesterday.strftime("%Y/%m/%d").replace("/","-")
#print(today_str)


hold_url_list = []
target_url = []
url_list = []
minrepo_dict = {}
#exit(0)



past_date = fourteendays(15)
# print(past_date)

# 東京都の店舗一覧
with codecs.open('D://myVSCodeProg//AI//test//dataonline//hall_list.txt', 'r', 'utf_8') as f:
    hall_url_list = f.readlines()


# hallごとのURLにアクセス
for hall in hall_url_list:
    header, proxy = ua_and_proxy_set_func()
    print("header:{},proxy:{}".format(header, proxy))

    hall = hall.strip()
    hall_id = hall.replace("https://daidata.goraggio.com/", "")
    # 台番一覧URL格納用
    daiban_page = []

    soup = soup_get_func_retry(hall, header, proxy)
    print(hall)
    print(soup.find_all("title")[0].text)
    # 台番一覧ページ取得
    for li in soup.find_all("li", class_="Radius-Basic"):
        for a in li.find_all("a"):
            if "台番号" in a.text:
                #print(a.attrs["href"])
                daiban_page.append(a.attrs["href"])

    # パチンコパチスロ全台の個別URLを取得
    for ps in daiban_page:
        #print(ps)
        # 個別URL格納用
        unit_url_list = []
        soup = soup_get_func_retry(ps, header, proxy)
        #past_date = []
        past_page = []
        # 過去の日付とページ番号を取得
        for op in soup.find_all("option"):
            #past_date.append(op.text)
            past_page.append(op["value"])
        #print(past_date)
        #print(past_page)
        #exit(0)
        hall_path = "D:\\myVSCodeProg\\AI\\test\\dataonline\\html\\" + str(hall_id)
        print(hall_path)
        check = directory(hall_path, hall_id)
        ps_dir = None

        if "P" == ps[-1]:
            ps_dir = hall_path + "\\" + "P"
        elif "S" == ps[-1]:
            ps_dir = hall_path + "\\" + "S"
        else:
            print("URL error")
            print(ps)
            exit(0)
        directory(ps_dir, ps[-1])

        #if not check:
        #    continue

        # 日付ごとの処理
        for k,date in enumerate(past_date):
            # その日付のフォルダが無ければhtml取得していないので取得しに行く。ただし当日は取らない
            if date == today_str:
                print("当日のデータは取得しない。%s" % today_str)
                continue

            # 保存先ディレクトリの確認
            store_path = ps_dir + "\\" + str(date)
            print(store_path)
            # あったら次の日付に移行
            # 無ければディレクトリ作成して続行
            check = directory(store_path, date)
            print(check)
            if check == False:
                continue
            elif check == True:
                unit_url_list = unit_html_get(unit_url_list, soup, date, header, proxy, store_path, hall_id)

            countdown_timer(0, 5)
            print("hall:%s\ndate:%s\nps:%s" %(hall_id, date, ps[-1]))

print("ALL FINISH!!")
