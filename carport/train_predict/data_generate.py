from carport.data import dbutil as db
import pandas as pd
# chepai_dic = db.queryCarsInfo()
def data_gr(chepai_dic):
    chepai_names = list(chepai_dic.keys())
    dataframe_list = []
    for name in chepai_names:
        data_name = name
        data_values = chepai_dic[data_name]
        data_num = len(data_values)

        rc_list = []
        cc_list = []
        for i in range(data_num):
            data_value = data_values[i]
            rc_list.append(data_value[0])
            cc_list.append(data_value[1])

        dataframe = pd.DataFrame({"车牌号":data_name,"入场时间":rc_list,"出场时间":cc_list})
        dataframe_list.append(dataframe)
    return dataframe_list

if __name__ == "__main__":
    chepai_dic = db.queryCarsInfo()
    dataframe_list = data_gr(chepai_dic)
    print(dataframe_list[0])


