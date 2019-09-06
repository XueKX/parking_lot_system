from sklearn.externals import joblib
import numpy as np
from carport.data import dbutil as db
from carport.train_predict.data_generate import *
from carport.train_predict.data_pro import *
import random
from keras.backend import clear_session


# 1.加载可用的数据
path_model_dir_tree = "C:/Users/wangquan/Desktop/tree/model/"
path_model_dir_xgboost = "C:/Users/wangquan/Desktop/xgboost/model/"
path_model_dir_lstm = "C:/Users/wangquan/Desktop/lstm/model/"
path_log = "C:/Users/wangquan/Desktop/ensemble/log.txt"
path_yuce_dir = "C:/Users/wangquan/Desktop/ensemble/"


names_not_inuse_path = path_model_dir_tree + "names_not_inuse.m"
names_not_inuse = joblib.load(names_not_inuse_path)

# 2.加载数据库的数据集
chepai_dic = db.queryCarsInfo()
dataframe_list = data_gr(chepai_dic)

# 3.生成
def predict_tree(model,x_yece):
    pre_0class_value = model.predict_proba(x_yece)[0][0]
    return pre_0class_value

def predict_xgboost(model,x_yece):
    pre_0class_value = model.predict_proba(x_yece)[0][0]
    return pre_0class_value

def predict_lstm(model,x_yece):
    y_pre = model.predict(x_yece)
    y_pre = 1- y_pre.reshape(len(y_pre), )
    return y_pre

def predicts_ensemble(names_not_inuse,dataframe_list,path_model_dir_tree,path_model_dir_xgboost,path_model_dir_lstm,path_log,path_yuce_dir):
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

            yuce_value_list_tree = []
            yuce_value_list_xgboost = []
            yuce_value_list_lstm = []

            for j in range(24):
                model_path_tree =  path_model_dir_tree + chepai_name + "_" + str(j) + "_model.m"
                model_tree = joblib.load(model_path_tree)
                yuce_tree = predict_tree(model_tree,x_yuce)
                yuce_value_list_tree.append(yuce_tree)

                model_path_xgboost = path_model_dir_xgboost + chepai_name + "_" + str(j) + "_model.m"
                model_xgboost = joblib.load(model_path_xgboost)
                yuce_xgboost = predict_xgboost(model_xgboost, x_yuce)
                yuce_value_list_xgboost.append(yuce_xgboost)



                model_path_lstm = path_model_dir_lstm + chepai_name + "_" + str(j) + "_model.m"
                model_lstm = joblib.load(model_path_lstm)
                yuce_lstm = predict_lstm(model_lstm, x_yuce)
                yuce_lstm = yuce_lstm[0]
                if yuce_lstm < 0:
                    yuce_lstm = round(random.uniform(0.1, 0.3), 2)
                elif yuce_lstm > 1:
                    yuce_lstm = round(random.uniform(0.7, 0.95), 2)


                yuce_value_list_lstm.append(yuce_lstm)
                clear_session()

            yuce_value_list = 0.2*np.array(yuce_value_list_tree) + 0.5*np.array(yuce_value_list_xgboost) + 0.3*np.array(yuce_value_list_lstm)

            data_pre = pd.DataFrame({"车牌号":chepai_name,"未来24小时车位闲置概率":yuce_value_list})
            data_save_path = path_yuce_dir + chepai_name + "_ensemble_pre.csv"
            data_pre.to_csv(data_save_path, index=False, encoding='utf_8_sig')

if __name__ == "__main__":
    predicts_ensemble(names_not_inuse, dataframe_list, path_model_dir_tree, path_model_dir_xgboost, path_model_dir_lstm,
                      path_log, path_yuce_dir)