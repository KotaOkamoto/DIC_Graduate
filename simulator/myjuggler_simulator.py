# -*- coding: utf-8 -*-
# マイジャグラーのシミュレートを行うプログラム

# ライブラリのインポート
from myjuggler_proba import *
import os

# シミュレートする関数
# 無理やり書いてるのでもっときれいにしたい
def simulate(simulator, medals, total_BB, total_RB, total_grape, total_samai, max_samai, max_game, min_samai, min_game, mode=6, game=8000):
    table = np.zeros(65536)
    df = simulator.iloc[mode-1]
    cnt = 0
    for i in range(len(df.keys())):
        for j in range(df[i]):
            table[cnt] = i
            cnt += 1
    #print(np.unique(init_table, return_counts=True))
    medal = 0
    disp_game = 0
    bonus_get = -1
    store_dict = {}
    all_game = [0,]
    game_role = ["none",]
    samai = [0,]
    disp_game_list = [0,]
    cnt_BB = 0
    cnt_RB = 0
    cnt_grape = 0
    for i in range(1, game+1):
        medal -= 3
        bonus_lamp = -1
        choice = np.random.randint(0,65536)
        id = int(table[choice])
        role = df.keys()[id]
        disp_game += 1
        if id == 9:
            cnt_grape += 1
        elif id == 0 or id == 2 or id == 4:
            cnt_BB += 1
        elif id == 1 or id == 3:
            cnt_RB += 1

        if 0 <= id <= 4:
            bonus_lamp = 1
            if 2 <= id <= 3:
                medal += 2
            elif id == 4:
                medal += 1

        if bonus_lamp == 1:
            #print("{}G -- 表示G:{} -- 成立役:{} -- {} -- 差枚:{}".format(i, disp_game, role, id, medal))
            all_game.append(i)
            game_role.append(role)
            samai.append(medal)
            disp_game_list.append(disp_game)
            b_model = bonus_esta()
            b_table = calc(b_model)
            b = 0
            while bonus_get == -1:
                medal -= 1
                b_choice = np.random.randint(0, 65536)
                b_id = int(b_table[b_choice])
                b_role = b_model.keys()[b_id]
                if b_id == 0:
                    medal += 1
                elif b_id ==3:
                    medal += 15
                else:
                    medal += medals[role]
                    bonus_get = 1
                b += 1
                #print("-----成立後{}G目 -- 成立役：{} -- 差枚：{}".format(b, b_role, medal))
                all_game.append(i)
                game_role.append(b_role)
                samai.append(medal)
                disp_game_list.append("成立後{}G".format(b))

        if bonus_lamp == 1 and bonus_get == 1:
            disp_game = 0
            bonus_get = -1
            continue


        medal += medals[role]
        #print("{}G -- 表示G:{} -- 成立役:{} -- {} -- 差枚:{}".format(i, disp_game, role, id, medal))
        all_game.append(i)
        game_role.append(role)
        samai.append(medal)
        disp_game_list.append(disp_game)

    max_s = max(samai)
    if max_s == 0:
        max_g = 0
    else:
        #print("----------------maxgame: {}---------------".format(max_s))
        #print(len(samai))
        max_g = samai.index(max_s)

    min_s = min(samai)
    if min_s == 0:
        min_g = 0
    else:
        min_g = samai.index(min_s)

    #print(samai)
    print("mode: {}, game: {}, BB: {}, RB: {}, grape: {}, samai: {},max: {}, maxG: {}, min: {}, minG: {}".format(mode, game, cnt_BB, cnt_RB, cnt_grape, samai[-1], max_s, max_g, min_s, min_g))
    total_BB.append(cnt_BB)
    total_RB.append(cnt_RB)
    total_grape.append(cnt_grape)
    total_samai.append(samai[-1])
    max_samai.append(max_s)
    max_game.append(max_g)
    min_samai.append(min_s)
    min_game.append(min_g)
    store_dict["回転数"] = all_game
    store_dict["表示G数"] = disp_game_list
    store_dict["成立役"] = game_role
    store_dict["差枚数"] = samai


    # dfにして並び変え
    store_df = pd.DataFrame(store_dict)
    return store_df, total_BB, total_RB, total_grape, total_samai, max_samai, max_game, min_samai, min_game


# ボーナス成立から揃えるまでの挙動を管理する関数
def bonus_esta():
    b_rep = ["7.30", "7.30", "7.30", "7.30", "7.30", "7.30"]
    b_pierrot = ["1024.00", "1024.00", "1024.00", "1024.00", "1024.00", "1024.00"]
    b_bell = ["1024.00", "1024.00", "1024.00", "1024.00", "1024.00", "1024.00"]
    b_grape = ["28.00", "28.00", "28.00", "28.00", "28.00", "28.00"]
    b_corn_cherry = ["36.03", "35.95", "34.69", "33.51", "33.40", "33.23"]

    b_tmp = {}
    b_tmp["rep"] = [int(decimal_half_up(65536 / float(p))) for p in b_rep]
    b_tmp["pierrot"] = [int(decimal_half_up(65536 / float(p))) for p in b_pierrot]
    b_tmp["bell"] = [int(decimal_half_up(65536 / float(p))) for p in b_bell]
    b_tmp["grape"] = [int(decimal_half_up(65536 / float(p))) for p in b_grape]
    b_tmp["corn_cherry"] = [int(decimal_half_up(65536 / float(p))) for p in b_corn_cherry]

    tmp_df = pd.DataFrame.from_dict(b_tmp, orient="index").T
    bonus = pd.Series((65536 - tmp_df.sum(axis=1)), name="bonus")
    tmp_df = pd.concat((tmp_df, bonus), axis=1)

    return tmp_df


# dfからテーブルを生成する関数
def calc(simulator, mode=6):
    table = np.zeros(65536)
    df = simulator.iloc[mode - 1]
    cnt = 0
    for i in range(len(df.keys())):
        for j in range(df[i]):
            table[cnt] = i
            cnt += 1

    return table



if __name__ == "__main__":

    # 設定毎の成立確率をリストにする
    solo_BB = ["402.06", "397.19", "383.25", "372.36", "352.34", "334.37"]
    corn_cherry_BB = ["1456.36", "1394.38", "1337.47", "1260.30", "1213.63", "1170.29"]
    center_cherry_BB = ["6553.60", "6553.60", "6553.60", "6553.60", "6553.60", "6553.60"]
    solo_RB = ["668.73", "528.52", "496.48", "409.60", "390.10", "334.37"]
    corn_cherry_RB = ["1213.63", "1170.29", "1092.27", "1024.00", "963.76", "862.32"]
    rep = ["7.30", "7.30", "7.30", "7.30", "7.30", "7.30"]
    center_cherry = ["6553.60", "6553.60", "6553.60", "6553.60", "6553.60", "6553.60"]
    pierrot = ["1024.00", "1024.00", "1024.00", "1024.00", "1024.00", "1024.00"]
    bell = ["1024.00", "1024.00", "1024.00", "1024.00", "1024.00", "1024.00"]
    grape = ["6.35", "6.28", "6.25", "6.23", "6.17", "6.07"]
    corn_cherry = ["36.03", "35.95", "34.69", "33.51", "33.40", "33.23"]


    # それぞれのリストを1/65536のテーブルにアジャストして辞書に格納
    simulator = {}
    simulator["solo_BB"] = [int(decimal_half_up(65536 / float(p))) for p in solo_BB]
    simulator["solo_RB"] = [int(decimal_half_up(65536 / float(p))) for p in solo_RB]
    simulator["corn_cherry_BB"] = [int(decimal_half_up(65536 / float(p))) for p in corn_cherry_BB]
    simulator["corn_cherry_RB"] = [int(decimal_half_up(65536 / float(p))) for p in corn_cherry_RB]
    simulator["center_cherry_BB"] = [int(decimal_half_up(65536 / float(p))) for p in center_cherry_BB]
    simulator["rep"] = [int(decimal_half_up(65536 / float(p))) for p in rep]
    simulator["center_cherry"] = [int(decimal_half_up(65536 / float(p))) for p in center_cherry]
    simulator["pierrot"] = [int(decimal_half_up(65536 / float(p))) for p in pierrot]
    simulator["bell"] = [int(decimal_half_up(65536 / float(p))) for p in bell]
    simulator["grape"] = [int(decimal_half_up(65536 / float(p))) for p in grape]
    simulator["corn_cherry"] = [int(decimal_half_up(65536 / float(p))) for p in corn_cherry]


    # データフレーム化
    # 成立役で65536に満たない分は外れとして埋める -> "none"
    main_df = pd.DataFrame.from_dict(simulator, orient="index").T
    none = pd.Series((65536 - main_df.sum(axis=1)),name="none")
    main_df = pd.concat((main_df, none), axis=1)
    #print(main_df.sum(axis=1))


    # メダル増減値　今回はベルとピエロは全外しするので0に設定
    medals = {}
    medals["solo_BB"] = 312
    medals["corn_cherry_BB"] = 312
    medals["center_cherry_BB"] = 312
    medals["solo_RB"] = 104
    medals["corn_cherry_RB"] = 104
    medals["rep"] = 3
    medals["center_cherry"] = 1
    medals["pierrot"] = 0
    medals["bell"] = 0
    medals["grape"] = 7
    medals["corn_cherry"] = 2
    medals["none"] = 0


    # 設定のリスト、ハナビとかの場合は(1,5)とかにする？[1,2,5,6]の方が良いか
    mode_list = np.arange(1,7)

    # シミュレートゲーム数のリスト　(low, high, (size))　今回は500から9000までをランダムで(10000,)のサイズで生成
    total_game_list = np.random.randint(500, 9000, (10000, ))


    # シミュレート開始
    """
    ① 一回のシミュレートごとに全ゲームの履歴を残す
    ② 設定とゲーム数毎にローカルのディレクトリで管理
    ③ ②とは別に設定毎に生成されたデータを整理してまとめたcsvを出力する
    
    len(mode) * len(total_geme_list) * range()　個のデータが生成される
    """
    # 設定ごとにforが回る
    cnt = 0
    total_dict = {}
    for i in mode_list:
        mode_list = []
        totalgame = []
        total_BB = []
        total_RB = []
        total_grape = []
        total_samai = []
        max_samai = []
        max_game = []
        min_samai = []
        min_game = []

        # random.randintで生成したndarray分回る
        for j in total_game_list:
            print("simulate start! mode:{} game: {}".format(i, j))

            # それを更に複数作るためのfor 例：8000回転回った台のデータが100台欲しい、など
            # range()を変更すれば、同じ回転数でのシミュレートデータが複数個出てくる
            for k in range(1):
            # for k in range(200):
                mode_list.append(i)
                totalgame.append(j)
                store_dir = "./sim_data/mode_" + str(i)
                # store_dir = "./sim_data/mode_" + str(i) + "_" + str(j)
                if not os.path.exists(store_dir):
                    os.mkdir(store_dir)
                os.chdir(store_dir)
                # 冗長すぎる、、一回辞書にまとめれば良かった
                store_df, total_BB, total_RB, total_grape, total_samai, max_samai, max_game, min_samai, min_game = simulate(
                                                                                  main_df, medals, total_BB, total_RB,
                                                                                  total_grape, total_samai, max_samai,
                                                                                  max_game, min_samai, min_game, mode=i,
                                                                                  game=j)
                # 保存
                # csv_path = "random_simulate_mode_" + str(i) + "_" + str(j) + "G_" + str(cnt) + ".csv"
                csv_path = "simulate_mode_" + str(i) + "_" + str(j) + "G_" + str(k) + ".csv"
                store_df.to_csv(csv_path, index=False)
                cnt += 1
                print("simulation over. mode: {}, game: {}, cnt: {}".format(i, j, k))

            # 一旦辞書に格納してからまとめてdataframe化
            os.chdir("./sim_data/")
            total_dict["mode"] = mode_list
            total_dict["game"] = totalgame
            total_dict["total_BB"] = total_BB
            total_dict["total_RB"] = total_RB
            total_dict["total_grape"] = total_grape
            total_dict["total_samai"] = total_samai
            total_dict["max_samai"] = max_samai
            total_dict["max_game"] = max_game
            total_dict["min_samai"] = min_samai
            total_dict["min_game"] = min_game
            total_df = pd.DataFrame(total_dict)
            # 保存
            total_path = "random_simulate_" + str(i) + "data" + ".csv"
            # total_path = "simulate_mode_" + str(i) + "data" + ".csv"
            total_df.to_csv(total_path, index=False)






