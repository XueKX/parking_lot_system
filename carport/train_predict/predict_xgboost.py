# from sklearn.model_selection import train_test_split
# from sklearn.tree import DecisionTreeClassifier
# from sklearn.metrics import confusion_matrix
# from sklearn.externals import joblib
# import numpy as np
# path_model_dir = "G:/wangquan/project_newland/tcw/model/xgboost/1-1-301/"
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
#
#
#
#
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import confusion_matrix
from sklearn.externals import joblib
import numpy as np
from carport.data import dbutil as db
from carport.train_predict.data_generate import *
from carport.train_predict.data_pro import *
# 1.加载可用的数据
path_model_dir = "C:/Users/wangquan/Desktop/xgboost/model/"
path_yuce_dir ="C:/Users/wangquan/Desktop/xgboost/test_result/"
path_log = "C:/Users/wangquan/Desktop/xgboost/log/log.txt"

names_not_inuse_path = path_model_dir + "names_not_inuse.m"
names_not_inuse = joblib.load(names_not_inuse_path)

# 2.加载数据库的数据集
chepai_dic = db.queryCarsInfo()
dataframe_list = data_gr(chepai_dic)

# 3.生成

def predict_xgboost(model,x_yece):
    pre_0class_value = model.predict_proba(x_yece)[0][0]
    return pre_0class_value




def predicts_xgboost(names_not_inuse,dataframe_list,path_model_dir,path_log,path_yuce_dir):
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
                yuce = predict_xgboost(model,x_yuce)
                yuce_value_list.append(yuce)
            data_pre = pd.DataFrame({"车牌号":chepai_name,"未来24小时车位闲置概率":yuce_value_list})
            data_save_path = path_yuce_dir + chepai_name + "_xgboost_pre.csv"
            data_pre.to_csv(data_save_path, index=False, encoding='utf_8_sig')

if __name__ == "__main__":
    predicts_xgboost(names_not_inuse, dataframe_list, path_model_dir, path_log, path_yuce_dir)































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



