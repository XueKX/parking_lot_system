import os
from carport.data import dbutil as db

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedShuffleSplit

# def train_read_data(path):
#     data = pd.read_csv(path, engine='python', encoding='gbk')
#     return data

# def train_read_data(data_list):
#     ruchang_chepai = []
#     ruchang_shijian = []
#     chuchang_shijian = []
#     num_data = len(data_list)
#     for i in range(num_data):
#         data01 = data_list[i]
#         ruchang_chepai.append(data01[0])
#         ruchang_shijian.append(data01[1])
#         chuchang_shijian.append(data01[2])
#     data = pd.DataFrame({"入场车牌":ruchang_chepai,"入场时间":ruchang_shijian,"出场时间":chuchang_shijian})
#     return data
# def train_read_data(data_list):
#     ruchang_shijian = []
#     chuchang_shijian = []
#     num_data = len(data_list)
#     for i in range(num_data):
#         data01 = data_list[i]
#         ruchang_shijian.append(data01[0])
#         chuchang_shijian.append(data01[1])
#     data = pd.DataFrame({"入场时间":ruchang_shijian,"出场时间":chuchang_shijian})
#     return data

def data_model(rc,cc):
    data_fz = pd.DataFrame({"入场时间":rc,"出场时间":cc})
    return data_fz

def data_rebuild(data_values,jg):
    xx = []
    yy = []
    num = len(data_values)
    for i in range(num-168-24):
        aa = list(data_values[i:i+168])
        bb = data_values[i+168+jg]
        xx.append(aa)
        yy.append(bb)
    return np.array(xx),np.array(yy)



def train_data_main(data):
    # data = train_read_data(data_list)
    rc = list(data["入场时间"])
    cc = list(data["出场时间"])
    data_fz = data_model(rc, cc)


    ewqi = pd.DataFrame({"入场时间": [data_fz.loc[0]["入场时间"].split(" ")[0] + " " + "00:00:01"]})
    ewqi["入场时间"] = pd.to_datetime(ewqi["入场时间"])



    rc01 = list(data_fz["入场时间"])
    cc01 = list(data_fz["出场时间"])
    num01 = len(rc01)
    r_c_c = []
    for i in range(num01):
        rr = rc01[i]
        cc = cc01[i]
        r_c_c.append(rr)
        r_c_c.append(cc)
    data_r_c = pd.DataFrame({"入出场时间": r_c_c})
    data_r_c["入出场时间"] = pd.to_datetime(data_r_c["入出场时间"])
    data_r_c_02 = list(data_r_c["入出场时间"] - ewqi["入场时间"][0])
    data_r_c_03 = []
    for sj in data_r_c_02:
        sj = str(sj)
        sj_l = sj.split(" ")
        sj_d = int(sj_l[0])
        sj_h_m = sj_l[2]
        sj_h = int(sj_h_m.split(":")[0])
        sj_m = int(sj_h_m.split(":")[1])
        sj_d_h_m = sj_d * 24 + sj_h + round(sj_m / 60, 1)
        data_r_c_03.append(sj_d_h_m)
    data_r_c_04 = pd.DataFrame({"入出场时间": data_r_c_03})

    # 在第一次入场之前的时间段，应该是空着的位置
    chushi = int(data_r_c_04["入出场时间"][0])
    ewai_dir = {}
    for i in range(chushi):
        kkk = str(i) + "-" + str(i + 1)
        ewai_dir[kkk] = 0

    time_list = list(data_r_c_04["入出场时间"])
    num01 = len(time_list)
    time_dir = {}
    for i in range(num01 - 1):
        if i % 2 == 0:
            a = time_list[i]
            b = time_list[i + 1]
            a_int = int(a)
            b_int = int(b)
            if a_int == b_int:
                kk = str(a_int) + "-" + str(a_int + 1)
                time_dir[kk] = 1
            elif a_int < b_int:
                jg = b_int - a_int
                for j in range(jg + 1):
                    kk = str(a_int) + "-" + str(a_int + 1)
                    time_dir[kk] = 1
                    a_int = a_int + 1
        else:
            a = time_list[i]
            b = time_list[i + 1]
            a_int = int(a)
            b_int = int(b)
            if a_int == b_int:
                kk = str(a_int) + "-" + str(a_int + 1)
                if kk in list(time_dir.keys()):
                    continue
                elif kk not in list(time_dir.keys()):
                    time_dir[kk] = 0
            elif a_int < b_int:
                jg = b_int - a_int
                for j in range(jg + 1):
                    kk = str(a_int) + "-" + str(a_int + 1)
                    if kk in list(time_dir.keys()):
                        a_int = a_int + 1
                        continue
                    elif kk not in list(time_dir.keys()):
                        kk = str(a_int) + "-" + str(a_int + 1)
                        time_dir[kk] = 0
                        a_int = a_int + 1
    for k, vall in time_dir.items():
        ewai_dir[k] = vall
    data_r_c_05 = pd.DataFrame({"时间段": list(ewai_dir.keys()), "车位是否空": list(ewai_dir.values())})
    data_r_c_06 = data_r_c_05["车位是否空"].values



    x_train_list = []
    x_test_list = []
    y_train_list = []
    y_test_list = []
    for i in range(24):
        x, y = data_rebuild(data_r_c_06, i)
        num_1= np.sum(y)
        num_00= len(y) - num_1
        if num_1==len(y):
            continue
        if num_00==len(y):
            continue
        if num_1/num_00<=0.2:
            continue
        if num_00/num_1<=0.2:
            continue
        if num_1<=10:
            continue
        if num_00<=10:
            continue
        # print("aa",i,num_1,num_00)
        sss = StratifiedShuffleSplit(n_splits=3, test_size=0.2, random_state=0)
        train_index_sum = []
        test_index_sum = []
        for train_index, test_index in sss.split(x, y):
            train_index_sum.append(train_index)
            test_index_sum.append(test_index)
        x_train = x[train_index_sum[0]]
        y_train = y[train_index_sum[0]]
        x_test = x[test_index_sum[0]]
        y_test = y[test_index_sum[0]]
        x_train_list.append(x_train)
        x_test_list.append(x_test)
        y_train_list.append(y_train)
        y_test_list.append(y_test)
    return x_train_list, x_test_list, y_train_list, y_test_list


def test_data_main(data):
    rc = list(data["入场时间"])
    cc = list(data["出场时间"])
    data_fz = data_model(rc, cc)

    ewqi = pd.DataFrame({"入场时间": [data_fz.loc[0]["入场时间"].split(" ")[0] + " " + "00:00:01"]})
    ewqi["入场时间"] = pd.to_datetime(ewqi["入场时间"])

    rc01 = list(data_fz["入场时间"])
    cc01 = list(data_fz["出场时间"])
    num01 = len(rc01)
    r_c_c = []
    for i in range(num01):
        rr = rc01[i]
        cc = cc01[i]
        r_c_c.append(rr)
        r_c_c.append(cc)
    data_r_c = pd.DataFrame({"入出场时间": r_c_c})
    data_r_c["入出场时间"] = pd.to_datetime(data_r_c["入出场时间"])
    data_r_c_02 = list(data_r_c["入出场时间"] - ewqi["入场时间"][0])
    data_r_c_03 = []
    for sj in data_r_c_02:
        sj = str(sj)
        sj_l = sj.split(" ")
        sj_d = int(sj_l[0])
        sj_h_m = sj_l[2]
        sj_h = int(sj_h_m.split(":")[0])
        sj_m = int(sj_h_m.split(":")[1])
        sj_d_h_m = sj_d * 24 + sj_h + round(sj_m / 60, 1)
        data_r_c_03.append(sj_d_h_m)
    data_r_c_04 = pd.DataFrame({"入出场时间": data_r_c_03})

    # 在第一次入场之前的时间段，应该是空着的位置
    chushi = int(data_r_c_04["入出场时间"][0])
    ewai_dir = {}
    for i in range(chushi):
        kkk = str(i) + "-" + str(i + 1)
        ewai_dir[kkk] = 0

    time_list = list(data_r_c_04["入出场时间"])
    num01 = len(time_list)
    time_dir = {}
    for i in range(num01 - 1):
        if i % 2 == 0:
            a = time_list[i]
            b = time_list[i + 1]
            a_int = int(a)
            b_int = int(b)
            if a_int == b_int:
                kk = str(a_int) + "-" + str(a_int + 1)
                time_dir[kk] = 1
            elif a_int < b_int:
                jg = b_int - a_int
                for j in range(jg + 1):
                    kk = str(a_int) + "-" + str(a_int + 1)
                    time_dir[kk] = 1
                    a_int = a_int + 1
        else:
            a = time_list[i]
            b = time_list[i + 1]
            a_int = int(a)
            b_int = int(b)
            if a_int == b_int:
                kk = str(a_int) + "-" + str(a_int + 1)
                if kk in list(time_dir.keys()):
                    continue
                elif kk not in list(time_dir.keys()):
                    time_dir[kk] = 0
            elif a_int < b_int:
                jg = b_int - a_int
                for j in range(jg + 1):
                    kk = str(a_int) + "-" + str(a_int + 1)
                    if kk in list(time_dir.keys()):
                        a_int = a_int + 1
                        continue
                    elif kk not in list(time_dir.keys()):
                        kk = str(a_int) + "-" + str(a_int + 1)
                        time_dir[kk] = 0
                        a_int = a_int + 1
    for k, vall in time_dir.items():
        ewai_dir[k] = vall
    data_r_c_05 = pd.DataFrame({"时间段": list(ewai_dir.keys()), "车位是否空": list(ewai_dir.values())})
    data_r_c_06 = data_r_c_05["车位是否空"].values


    test_data = []
    num_data_r_c_06 = len(data_r_c_06)
    xx = data_r_c_06[num_data_r_c_06-168:num_data_r_c_06]
    test_data.append(xx)
    return np.array(test_data)







