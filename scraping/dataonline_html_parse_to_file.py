# -*- coding: utf-8 -*-
# dataonlineのhtmlファイルを解析してファイル出力するためのプログラム

# ライブラリのインポート
from config import *
import zipfile

# 正規表現コンパイル
url_pattern = r"https://daidata.goraggio.com//[0-9]+"
num_pattern = r"\d+"
unit_pattern = r"unit_\d+"
date_pattern = r"\d{4}-\d{2}-\d{2}"

ng_word = ["対象日のデータは更新されていません","本日店休日となっております"]



def html_parser_pachinko(html_file):
    html = html_file.read()
    soup = BeautifulSoup(html, 'html.parser')
    for section in soup.find_all("section", class_="overview"):
        text = section.text
        if "対象日のデータは更新されていません" in text or "本日店休日となっております" in text:
            print("html error! {} NoData file!".format(unit_num))
            all_data_NaN_p()
            return
    # 店舗名と機種名を取得
    for title in soup.find_all("title"):
        text = title.text
        # print(text)
        if "FuelPHP Framework" in text:
            print("html error! {} Reacquire html file!!".format(unit_num))
            all_data_NaN_p()
            return
        elif "台データオンライン" in text:
            print("html error! {} NoData file!".format(unit_num))
            all_data_NaN_p()
            return
        text = text.strip().split("|")
        hall_name = text[0]
        model_name = text[1].replace(" - 台詳細", "")
        hall_name_list.append(hall_name)
        model_name_list.append(model_name)

    """
    dataframe解析
    基本的に8日間のデータがそれぞれ分かれている
    0 : 当日のBB,RB,ART,現在のG数
    1 : 最大持ち玉～合成確率の表
    2 : 当日の大当たり履歴
    3 : 当日のツブ
    4 : 前日のBB,RB,ART,現在のG数
    5 : 前日の最大持ち玉～合成確率の表
    以下表示されている最も古い日付まで続く
    ※店舗によって全く違うのでエラー発生する可能性あり。発生したら適宜調べること。
    """
    dfs = None
    try:
        dfs = pd.read_html(html)
        # print(len(dfs))
        # print(dfs)
        left_up = dfs[1].iloc[0, 0]
        # print(left_up)
        right_up = dfs[1].iloc[0, 2]
        # print(right_up)
        left_mid = dfs[1].iloc[1, 0]
        # print(left_mid)
        right_mid = dfs[1].iloc[1, 2]
        # print(right_mid)
        left_bottom = dfs[1].iloc[2, 0]
        # print(left_bottom)
        right_bottom = dfs[1].iloc[2, 2]
        # print(right_bottom)
        First_bonus_list.append(dfs[0].iloc[0, 0])
        Continue_list.append(dfs[0].iloc[0, 1])

        dfs_check(left_up, Max_Possession_list, dfs[1].iloc[0, 1])
        dfs_check(right_up, Total_Game_list, dfs[1].iloc[0, 3])
        dfs_check(left_mid, Bonus_propability_list, dfs[1].iloc[1, 1])
        dfs_check(right_mid, FinalGame_Day_Before_list, dfs[1].iloc[1, 3])
        dfs_check(left_bottom, Max_continue_list, dfs[1].iloc[2, 1])
        dfs_check(right_bottom, Max_continue_possession_list, dfs[1].iloc[2, 3])

    except IndexError as e:
        print(e)
        print("{} : table not found by pandas. No data file.".format(unit_num))
        all_data_NaN_p_2()
        return
    except ValueError as e:
        print(e)
        print("{} : No tables found by pandas. No data file.".format(unit_num))
        all_data_NaN_p_2()
        return

    except:
        print("{} : No tables found by pandas. No data file.".format(unit_num))
        all_data_NaN_p_2()
        return


    if not dfs and len(Hist_list) != 0:
        # print("not df, get table tag")
        pass
    elif not dfs and len(Hist_list) == 0:
        # print("not df")
        Hist_list.append("NaN")
    elif len(dfs) == 2:
        Hist_list.append("NaN")
    elif dfs[0].iloc[0, 0] != 0 or dfs[0].iloc[0, 1] != 0:
        Hist_list.append(dfs[2].values.tolist())
        # print(Hist_list)
    elif dfs[0].iloc[0, 0] == 0 and dfs[0].iloc[0, 1] == 0:
        Hist_list.append("NaN")

    for script in soup.find_all("script"):
        # print(script)
        if "日グラフ" in script.string:
            pattern = r"var\sdata\s=\s.+;"
            match = re.search(pattern, script.string)
            graph = match.group().rstrip(";")
            graph = graph.replace("var data = ", "")
            # print(graph)
            Day_Graph_list.append(graph)


def html_parser_slot(html_file):
    html = html_file.read()
    soup = BeautifulSoup(html, 'html.parser')
    for section in soup.find_all("section", class_="overview"):
        text = section.text
        if "対象日のデータは更新されていません" in text:
            print("html error! {} NoData file!".format(unit_num))
            all_data_NaN_s()
            return
    # 店舗名と機種名を取得
    for title in soup.find_all("title"):
        text = title.text
        if "FuelPHP Framework" in text:
            print("html error! {} Reacquire html file!!".format(unit_num))
            all_data_NaN_s()
            return
        elif "台データオンライン" in text:
            print("html error! {} NoData file!".format(unit_num))
            all_data_NaN_s()
            return
        text = text.strip().split("|")
        hall_name = text[0]
        model_name = text[1].replace(" - 台詳細", "")
        hall_name_list.append(hall_name)
        model_name_list.append(model_name)

    """
    dataframe解析
    基本的に8日間のデータがそれぞれ分かれている
    0 : 当日のBB,RB,ART,現在のG数
    1 : 最大持ち玉～合成確率の表
    2 : 当日の大当たり履歴
    3 : 当日のツブ
    4 : 前日のBB,RB,ART,現在のG数
    5 : 前日の最大持ち玉～合成確率の表
    以下表示されている最も古い日付まで続く
    """
    dfs = None
    try:
        dfs = pd.read_html(html)
        # print(len(dfs))
        # print(dfs[0].shape[1])
        # print(dfs)

        left_up = dfs[1].iloc[0, 0]
        # print(left_up)
        right_up = dfs[1].iloc[0, 2]
        # print(right_up)
        left_mid = dfs[1].iloc[1, 0]
        # print(left_mid)
        right_mid = dfs[1].iloc[1, 2]
        # print(right_mid)
        left_bottom = dfs[1].iloc[2, 0]
        # print(left_bottom)
        right_bottom = dfs[1].iloc[2, 2]
        # print(right_bottom)

        if dfs[0].shape[1] == 2:
            # print("OK")
            BB_list.append(dfs[0].iloc[0, 0])
            RB_list.append("NaN")
            ART_list.append("NaN")
        else:
            BB_list.append(dfs[0].iloc[0, 0])
            RB_list.append(dfs[0].iloc[0, 1])
            ART_list.append(dfs[0].iloc[0, 2])

        dfs_check(left_up, Max_Possession_list, dfs[1].iloc[0, 1])
        dfs_check(right_up, Total_Game_list, dfs[1].iloc[0, 3])
        dfs_check(left_mid, FinalGame_Day_Before_list, dfs[1].iloc[1, 1])
        dfs_check(right_mid, Composite_Probability_list, dfs[1].iloc[1, 3])
        dfs_check(left_bottom, BB_Probability_list, dfs[1].iloc[2, 1])
        dfs_check(right_bottom, RB_Probability_list, dfs[1].iloc[2, 3])

    except IndexError as e:
        print(e)
        print("{} : table not found by pandas.".format(unit_num))
        all_data_NaN_s_2()
        return

    except ValueError as e:
        print(e)
        print("{} : No tables found by pandas. No data file.".format(unit_num))
        all_data_NaN_s_2()
        return


    if not dfs and len(Hist_list) != 0:
        # print("not df, get table tag")
        pass
    elif not dfs and len(Hist_list) == 0:
        # print("not df")
        Hist_list.append("NaN")
    elif len(dfs) == 2:
        Hist_list.append("NaN")
    elif dfs[0].iloc[0, 0] != 0 or dfs[0].iloc[0, 1] != 0:
        Hist_list.append(dfs[2].values.tolist())
    elif dfs[0].iloc[0, 0] == 0 and dfs[0].iloc[0, 1] == 0:
        Hist_list.append("NaN")
    # print(Hist_list)
    for script in soup.find_all("script"):
        # print(script)
        if "日グラフ" in script.string:
            pattern = r"var\sdata\s=\s.+;"
            match = re.search(pattern, script.string)
            graph = match.group().rstrip(";")
            graph = graph.replace("var data = ", "")
            # print(graph)
            Day_Graph_list.append(graph)


def data_csv_check(file_path):
    if os.path.isfile(file_path):
        df = pd.read_csv(file_path)
        return df
    else:
        with codecs.open(file_path, "w", "utf-8") as f:
            pass


def zip_and_deleted_func(zip_path, file_list):
    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as new_zip:
        for file in file_list:
            new_zip.write(os.path.join(date_dir, file))
    for file in file_list:
        # print(file)
        if os.path.isfile(os.path.join(date_dir, file)):
            os.remove(os.path.join(date_dir, file))
    print("zip & remove over!!")


def dfs_check(index_text, append_list, data):
    if index_text != "NaN":
        append_list.append(data)
    else:
        append_list.append("NaN")


def all_data_NaN_p():
    hall_name_list.append("NaN")
    model_name_list.append("NaN")
    First_bonus_list.append("NaN")
    Continue_list.append("NaN")
    Max_Possession_list.append("NaN")
    Total_Game_list.append("NaN")
    Bonus_propability_list.append("NaN")
    FinalGame_Day_Before_list.append("NaN")
    Max_continue_list.append("NaN")
    Max_continue_possession_list.append("NaN")
    Hist_list.append("NaN")
    Day_Graph_list.append("NaN")

def all_data_NaN_p_2():
    First_bonus_list.append("NaN")
    Continue_list.append("NaN")
    Max_Possession_list.append("NaN")
    Total_Game_list.append("NaN")
    Bonus_propability_list.append("NaN")
    FinalGame_Day_Before_list.append("NaN")
    Max_continue_list.append("NaN")
    Max_continue_possession_list.append("NaN")
    Hist_list.append("NaN")
    Day_Graph_list.append("NaN")

def all_data_NaN_s():
    hall_name_list.append("NaN")
    model_name_list.append("NaN")
    BB_list.append("NaN")
    RB_list.append("NaN")
    ART_list.append("NaN")
    Max_Possession_list.append("NaN")
    Total_Game_list.append("NaN")
    FinalGame_Day_Before_list.append("NaN")
    Composite_Probability_list.append("NaN")
    BB_Probability_list.append("NN")
    RB_Probability_list.append("NaN")
    Hist_list.append("NaN")
    Day_Graph_list.append("NaN")


def all_data_NaN_s_2():
    BB_list.append("NaN")
    RB_list.append("NaN")
    ART_list.append("NaN")
    Max_Possession_list.append("NaN")
    Total_Game_list.append("NaN")
    FinalGame_Day_Before_list.append("NaN")
    Composite_Probability_list.append("NaN")
    BB_Probability_list.append("NN")
    RB_Probability_list.append("NaN")
    Hist_list.append("NaN")
    Day_Graph_list.append("NaN")


def table_parse(soup):
    th = []
    td = []
    unit_Hist_list = []
    for table in soup.find_all("table", class_="overviewTable"):
        for row in table.find_all("th"):
            text = row.text.translate(str.maketrans("","", "\n "))
            if "対象日のデータは更新されていません" in text:
                pass
            else:
                th.append(text)
        for row in table.find_all("td"):
            td.append(row.text.translate(str.maketrans("","", "\n ")))
    for table_2 in soup.find_all("table", class_="overviewTable3"):
        for row_2 in table_2.find_all("th"):
            th.append(row_2.text.translate(str.maketrans("","", "\n ")))
        for row_2_2 in table_2.find_all("td"):
            td.append(row_2_2.text.translate(str.maketrans("","", "\n ")))

    for table_3 in soup.find_all("table", class_="numericValueTable"):
        for row_3 in table_3.find_all("tr"):
            tr_list = []
            for td_3 in row_3.find_all("td"):
                tr_list.append(td_3.text.translate(str.maketrans("","", "\n \\")).strip())
                #print(tr_list)
            unit_Hist_list.append(tr_list)

    Hist_list.append(unit_Hist_list)
    #print(th)
    #print(td)
    if len(th) == 0:
        return
    for i,v in enumerate(th):
        if "大当たり" in v:
            First_bonus_list.append(td[i])
        elif "確変" in v:
            Continue_list.append(td[i])
        elif "最大持玉" in v:
            Max_Possession_list.append(td[i])
        elif "累計スタート" in v:
            Total_Game_list.append(td[i])
        elif "初当たり確率" in v:
            Bonus_propability_list.append(td[i])
        elif "前日最終スタート" in v:
            FinalGame_Day_Before_list.append(td[i])
        elif "本日の最大連荘数" in v:
            Max_continue_list.append(td[i])
        elif "連荘最大出玉" in v:
            Max_continue_possession_list.append(td[i])
        elif "合成確率" in v:
            Composite_Probability_list.append(td[i])
        elif "BB確率" in v:
            BB_Probability_list.append(td[i])
        elif "RB確率" in v:
            RB_Probability_list.append(td[i])
        elif "BB" in v:
            BB_list.append(td[i])
        elif "RB" in v:
            RB_list.append(td[i])
        elif "ART" in v:
            ART_list.append(td[i])
        else:
            pass


def list_length_comp(list_list, length):
    print("row : {}".format(length))
    for i,l in list_list.items():
        if len(l) == length:
            print("data size : {}".format(len(l)))
            print("{} : size OK!".format(i))
        elif len(l) > length:
            print("data size : {}".format(len(l)))
            print("{} : size NG, too big!".format(i))
        elif len(l) == 0:
            print("data size : {}".format(len(l)))
            print("{} : no data, fill in for NaN".format(i))
            for i in range(length):
                l.append("NaN")
            print("full fill NaN!")
        elif len(l) < length:
            print("data size : {}".format(len(l)))
            print("{} : size NG, too short!".format(i))

    print("再チェック！")
    for i,l in list_list.items():
        if len(l) == length:
            print("{} : size OK!".format(i))
        else:
            print("not same : {}".format(i))
    return list_list



date_list = []
hall_id_list = []
hall_name_list = []
unit_num_list = []
model_name_list = []
BB_list = []
RB_list = []
ART_list = []
Max_Possession_list = []
Total_Game_list = []
FinalGame_Day_Before_list = []
Composite_Probability_list = []
BB_Probability_list = []
RB_Probability_list = []
Day_Graph_list = []
First_bonus_list = []
Continue_list = []
Max_Possession_list = []
Total_Game_list = []
Bonus_propability_list = []
FinalGame_Day_Before_list = []
Max_continue_list = []
Max_continue_possession_list = []
Hist_list = []


all_pachinko_list = {"date_list":date_list, "hall_id_list":hall_id_list, "hall_name_list":hall_name_list,
                     "unit_num_list":unit_num_list, "model_name_list":model_name_list, "Day_Graph_list":Day_Graph_list,
                     "First_bonus_list":First_bonus_list, "Continue_list":Continue_list,
                     "Max_Possession_list":Max_Possession_list, "Total_Game_list":Total_Game_list,
                     "Bonus_propability_list":Bonus_propability_list,
                     "FinalGame_Day_Before_list":FinalGame_Day_Before_list, "Max_continue_list":Max_continue_list,
                     "Max_continue_possession_list":Max_continue_possession_list, "Hist_list":Hist_list}

all_slot_list = {"date_list":date_list, "hall_id_list":hall_id_list, "hall_name_list":hall_name_list,
                     "unit_num_list":unit_num_list, "model_name_list":model_name_list, "Day_Graph_list":Day_Graph_list,
                     "BB_list":BB_list, "RB_list":RB_list, "ART_list":ART_list, "First_bonus_list":First_bonus_list,
                     "Continue_list":Continue_list,
                     "Max_Possession_list":Max_Possession_list, "Total_Game_list":Total_Game_list,
                     "Composite_Probability_list":Composite_Probability_list, "BB_Probability_list":BB_Probability_list,
                     "RB_Probability_list":RB_Probability_list,
                     "FinalGame_Day_Before_list":FinalGame_Day_Before_list, "Max_continue_list":Max_continue_list,
                     "Max_continue_possession_list":Max_continue_possession_list, "Hist_list":Hist_list}


# 最初に整理済みリストファイルをチェック
organize_file = "./dataonline/data_organizer.txt"
with codecs.open(organize_file, "r", "utf-8") as f:
    ok_list = f.read()
print(ok_list)

cur_path = "./dataonline/html"
hall_dir_list = dir_listup_func(cur_path)
# print(hall_dir_list)


# 一店舗だけ回す用
# hall_dir_list = ["./dataonline/html/100260"]


for hall_dir in hall_dir_list:
    ps_dir = dir_listup_func(hall_dir)
    #print(ps_dir)
    for ps in ps_dir:
        #print(ps)
        dir_list = dir_listup_func(ps)
        if str(ps[-1]) == "P":
            for date_dir in dir_list:
                if os.path.isdir(date_dir):
                    if date_dir in ok_list:
                        print("{} : organized! go to next folder!".format(date_dir))
                    else:
                        tmp_dict = {}
                        date_list = []
                        hall_id_list = []
                        hall_name_list = []
                        unit_num_list = []
                        model_name_list = []
                        BB_list = []
                        RB_list = []
                        ART_list = []
                        Max_Possession_list = []
                        Total_Game_list = []
                        FinalGame_Day_Before_list = []
                        Composite_Probability_list = []
                        BB_Probability_list = []
                        RB_Probability_list = []
                        Day_Graph_list = []
                        First_bonus_list = []
                        Continue_list = []
                        Max_Possession_list = []
                        Total_Game_list = []
                        Bonus_propability_list = []
                        FinalGame_Day_Before_list = []
                        Max_continue_list = []
                        Max_continue_possession_list = []
                        Hist_list = []
                        print("{} : データ整形開始".format(date_dir))
                        file_path = file_count_func(date_dir)
                        if "data.csv" in file_path:
                            print("discovery data.csv, This directory is completed?")
                            break
                        # print(file_path)
                        for unit_html in file_path:
                            unit = date_dir + "\\" + unit_html
                            # 台番号と日時とホールidはパスから取得
                            unit_num = re.search(unit_pattern, unit).group().replace("unit_", "")
                            unit_num_list.append(int(unit_num))
                            date = re.search(date_pattern, unit).group()
                            date_list.append(date)
                            hall_id = re.search(num_pattern, unit).group()
                            hall_id_list.append(hall_id)
                            print(hall_id, unit_num)
                            # それ以外はhtmlから取得する
                            with codecs.open(unit, "r", "utf-8") as f:
                                html_parser_pachinko(f)
                        # 取ってきたリストを辞書形式に。dfにするため。ここもっといい処理あったら変えたい。

                        list_length_comp(all_pachinko_list, len(file_path))
                        tmp_dict["date"] = date_list
                        tmp_dict["hall_id"] = hall_id_list
                        tmp_dict["hall_name"] = hall_name_list
                        tmp_dict["unit_num"] = unit_num_list
                        tmp_dict["model_name"] = model_name_list
                        tmp_dict["Bonus"] = First_bonus_list
                        tmp_dict["Continue"] = Continue_list
                        tmp_dict["Max_Possession"] = Max_Possession_list
                        tmp_dict["Total_Game"] = Total_Game_list
                        tmp_dict["First_Bonus_Propability"] = Bonus_propability_list
                        tmp_dict["FinalGame_Day_Before"] = FinalGame_Day_Before_list
                        tmp_dict["Max_continue"] = Max_continue_list
                        tmp_dict["Max_continue_possession"] = Max_continue_possession_list
                        tmp_dict["Day_Graph"] = Day_Graph_list
                        tmp_dict["Day_hist"] = Hist_list
                        for i, k in tmp_dict.items():
                            print("{} : {}".format(i, len(k)))
                        # dfにして並び変え
                        df = pd.DataFrame(tmp_dict)
                        df_s = df.sort_values('unit_num')
                        #print(df_s)
                        # 保存
                        csv_path = date_dir + "\\data.csv"
                        df_s.to_csv(csv_path, index=False)

                        zip_path = date_dir + "\\data.zip"
                        zip_and_deleted_func(zip_path, file_path)
                        with codecs.open(organize_file, "a", "utf-8") as f:
                            f.write(date_dir + "\n")
                        print("directory over!! : {}".format(date_dir))

                else:
                    print("This path is not directory. use only directory.")
                    continue

        elif str(ps[-1]) == "S":
            for date_dir in dir_list:
                if os.path.isdir(date_dir):
                    if date_dir in ok_list:
                        print("{} : organized! go to next folder!".format(date_dir))
                    else:
                        tmp_dict = {}
                        date_list = []
                        hall_id_list = []
                        hall_name_list = []
                        unit_num_list = []
                        model_name_list = []
                        BB_list = []
                        RB_list = []
                        ART_list = []
                        Max_Possession_list = []
                        Total_Game_list = []
                        FinalGame_Day_Before_list = []
                        Composite_Probability_list = []
                        BB_Probability_list = []
                        RB_Probability_list = []
                        Day_Graph_list = []
                        First_bonus_list = []
                        Continue_list = []
                        Max_Possession_list = []
                        Total_Game_list = []
                        Bonus_propability_list = []
                        FinalGame_Day_Before_list = []
                        Max_continue_list = []
                        Max_continue_possession_list = []
                        Hist_list = []
                        print("{} : データ整形開始".format(date_dir))
                        file_path = file_count_func(date_dir)
                        # print(file_path)
                        for unit_html in file_path:
                            unit = date_dir + "\\" + unit_html
                            # 台番号と日時とホールidはパスから取得
                            unit_num = re.search(unit_pattern, unit).group().replace("unit_", "")
                            unit_num_list.append(int(unit_num))
                            date = re.search(date_pattern, unit).group()
                            date_list.append(date)
                            hall_id = re.search(num_pattern, unit).group()
                            hall_id_list.append(hall_id)
                            print(hall_id, unit_num)
                            # それ以外はhtmlから取得する
                            with codecs.open(unit, "r", "utf-8") as f:
                                html_parser_slot(f)
                        # 取ってきたリストを辞書形式に。dfにするため。ここもっといい処理あったら変えたい。
                        list_length_comp(all_slot_list, len(file_path))
                        tmp_dict["date"] = date_list
                        tmp_dict["hall_id"] = hall_id_list
                        tmp_dict["hall_name"] = hall_name_list
                        tmp_dict["unit_num"] = unit_num_list
                        tmp_dict["model_name"] = model_name_list
                        tmp_dict["BB"] = BB_list
                        tmp_dict["RB"] = RB_list
                        tmp_dict["ART"] = ART_list
                        tmp_dict["Max_Possession"] = Max_Possession_list
                        tmp_dict["Total_Game"] = Total_Game_list
                        tmp_dict["FinalGame_Day_Before"] = FinalGame_Day_Before_list
                        tmp_dict["Composite_Probability"] = Composite_Probability_list
                        tmp_dict["BB_Probability"] = BB_Probability_list
                        tmp_dict["RB_Probability"] = RB_Probability_list
                        tmp_dict["Day_Graph"] = Day_Graph_list
                        tmp_dict["Day_hist"] = Hist_list
                        for i, k in tmp_dict.items():
                            print("{} : {}".format(i, len(k)))
                        # dfにして並び変え
                        df = pd.DataFrame(tmp_dict)
                        df_s = df.sort_values('unit_num')
                        # print(df_s)
                        # 保存
                        csv_path = date_dir + "\\data.csv"
                        df_s.to_csv(csv_path, index=False)

                        zip_path = date_dir + "\\data.zip"
                        zip_and_deleted_func(zip_path, file_path)

                        with codecs.open(organize_file, "a", "utf-8") as f:
                            f.write(date_dir + "\n")
                        print("directory over!! : {}".format(date_dir))
                else:
                    print("This path is not directory. use only directory.")
                    continue

#"""

print("ALL FINISH!!")
