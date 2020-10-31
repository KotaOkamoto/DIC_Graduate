# -*- coding: utf-8 -*-
# マイジャグラーの設定差を管理するプログラム

# ライブラリのインポート
import numpy as np
import pandas as pd


# マイジャグラーの設定差を管理するクラス
# ブドウ回数生成が主な用途
# ゲーム数、差枚、ボーナス回数が分かれば、ブドウを逆算することが出来る
class MyJuggler:
    def __init__(self, cherry=35.0):
        self.BB = ["287.4", "282.5", "273.1", "264.3", "252.1", "240.9"]
        self.RB = ["431.1", "364.1", "341.3", "292.6", "277.7", "240.9"]
        self.grape = ["6.35", "6.28", "6.25", "6.23", "6.17", "6.07"]
        self.rep = 7.3
        self.cherry = cherry
        self.setting_dict = {}
        pass

    def setting(self):
        self.setting_dict["BB_proba"] = [1 / float(p) for p in self.BB]
        self.setting_dict["RB_proba"] = [1 / float(p) for p in self.RB]
        self.setting_dict["grape_proba"] = [1 / float(p) for p in self.grape]
        self.setting_dict["label"] = np.arange(1, 7)

        setting_df = pd.DataFrame.from_dict(self.setting_dict, orient="index").T
        return self.setting_dict, setting_df

    def grape_calc_func(self, n_game=0, n_bb=0, n_rb=0, n_diff=0, n_cherry=0):

        n_bb = 1 if n_bb == 0 else n_bb
        n_rb = 1 if n_rb == 0 else n_rb
        n_diff = 1 if n_diff == 0 else n_diff
        n_cherry = 1 if n_cherry == 0 else n_cherry
        role_sum = n_bb + n_rb + n_cherry
        n_game = role_sum if n_game < role_sum else n_game

        out = n_game * 3 + n_diff
        if n_cherry < 2:
            n_cherry = int(n_game / self.cherry)
        tmp_in = n_bb * 312 + n_rb * 104 + decimal_half_up(n_game / self.rep * 3) + n_cherry * 2
        # print(out)
        # print(tmp_in)
        surplus = out - tmp_in
        # print(surplus)
        n_grape = decimal_half_up(surplus / 7)
        n_grape = 0 if n_grape < 0 else n_grape

        return n_grape


#test = MyJuggler()
#grape = test.grape_calc_func(8000, 30, 35, 1000, 0)
#print(grape)
