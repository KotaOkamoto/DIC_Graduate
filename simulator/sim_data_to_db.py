# -*- coding: utf-8 -*-
# シミュレートデータを成形してファイル出力するためのプログラム

# ライブラリのインポート
import numpy as np
import pandas as pd
import os
import glob



cur_dir = "./sim_data/"
os.chdir(cur_dir)
f_list = glob.glob("*.csv")
print(f_list)

pattern = r"random_simulate"
pattern2 = r"mode_1data"
pattern3 = r"random_simulate_five_2data"

# 最初のひとつをマスターとして、次回以降のデータをsub_dfにしてからconcat
for f in f_list:
    if re.match(pattern, f):
        if re.search(pattern3, f):
            master = pd.read_csv(f)
        else:
            sub = pd.read_csv(f)
            master = pd.concat([master, sub])
    else:
        pass

# print(master)
# print(master.describe())

master.to_csv("DB.csv")


