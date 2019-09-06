
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import confusion_matrix
from sklearn.externals import joblib
import numpy as np
from carport.data import dbutil as db
from carport.train_predict.data_generate import *
from carport.train_predict.data_pro import *
from keras.backend import clear_session
import random
# 1.加载可用的数据
path_model_dir = "C:/Users/wangquan/Desktop/lstm/model/"
path_yuce_dir ="C:/Users/wangquan/Desktop/lstm/test_result/"
path_log = "C:/Users/wangquan/Desktop/lstm/log/log.txt"

names_not_inuse_path = path_model_dir + "names_not_inuse.m"
names_not_inuse = joblib.load(names_not_inuse_path)

# 2.加载数据库的数据集
chepai_dic = db.queryCarsInfo()
dataframe_list = data_gr(chepai_dic)

# 3.生成

def predict_lstm(model,x_yece):
    y_pre = model.predict(x_yece)
    y_pre = 1- y_pre.reshape(len(y_pre), )
    return y_pre




def predicts_lstm(names_not_inuse,dataframe_list,path_model_dir,path_log,path_yuce_dir):
    dataframe_num = len(dataframe_list)
    for i in range(dataframe_num):
        data = dataframe_list[i]
        chepai_name = list(data["车牌号"])[0]
        if chepai_name in names_not_inuse:
            cont = chepai_name + "没有建立相应的模型，因此无法对这个数据集进行预测"
            with open(path_log, "a") as reader:
                reader.write(cont + "\n")
        else:
            cont = chepai_name + "建立相应的模型，可进行预测"
            with open(path_log, "a") as reader:
                reader.write(cont + "\n")
            x_yuce = test_data_main(data)

            yuce_value_list = []
            for j in range(24):
                model_path =  path_model_dir + chepai_name + "_" + str(j) + "_model.m"
                model = joblib.load(model_path)
                yuce = predict_lstm(model,x_yuce)
                yuce = yuce[0]
                if yuce<0:
                    yuece = round(random.uniform(0.1,0.3),2)
                elif yuce>1:
                    yuece = round(random.uniform(0.7,0.95),2)
                yuce_value_list.append(yuce)
                clear_session()
            data_pre = pd.DataFrame({"车牌号":chepai_name,"未来24小时车位闲置概率":yuce_value_list})
            data_save_path = path_yuce_dir + chepai_name + "_lstm_pre.csv"
            data_pre.to_csv(data_save_path, index=False, encoding='utf_8_sig')

if __name__ == "__main__":
    predicts_lstm(names_not_inuse, dataframe_list, path_model_dir, path_log, path_yuce_dir)































# path_model_dir = "G:/wangquan/project_newland/tcw/model/tree/1-1-301/"
# test_path = "G:/wangquan/project_newland/tcw/date_test/1-1-301/1-1-301.m"
# data_ce = joblib.load(test_path)
#
# yuce_sum = []
# for i in range(24):
#     model_path = path_model_dir + str(i) + "_model.m"
#     model_jz = joblib.load(model_path)
#     yuce = model_jz.predict(data_ce[i])
#     yuce_sum.append(yuce)
# yuece_sum = np.array(yuce_sum)
# print(yuece_sum)



