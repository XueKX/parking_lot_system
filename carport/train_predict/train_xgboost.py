
#
#
#
# def xgboost_train(x_train,y_train,x_test,y_test,args,properties):
#     auto_value =  properties["AUTO"]
#     bili = (len(y_train) - sum(y_train)) / sum(y_train)
#     if  auto_value==int(0):
#         logger = properties["LOGGER"]
#         logger.info("手调参模型开始训练")
#         max_depth_value = properties['MAX_DEPTH']
#         min_child_weight_value = properties['MIN_CHILD_WEIGHT']
#         gamma_value = properties['GAMMA']
#         subsample_value = properties['SUBSAMPLE']
#         colsample_bytree_value = properties['COLSAMPLE_BYTREE']
#         learning_rate_value = properties['LEARNING_RATE']
#         n_estimators_value = properties['N_ESTIMATORS']
#         status = properties['STATUS']
#         status.heartbeat(str(properties["FILE_PREFIX"]), "60%")
#
#         xgb_best = XGBClassifier(learning_rate=learning_rate_value,
#                                  n_estimators=n_estimators_value,
#                                  max_depth=max_depth_value,
#                                  gamma=gamma_value,
#                                  subsample=subsample_value,
#                                  colsample_bytree=colsample_bytree_value,
#                                  min_child_weight=min_child_weight_value,
#                                  scale_pos_weight=bili,
#                                  objective='binary:logistic')
#         xgb_best.fit(x_train, y_train)
#         # 存储xgboost模型
#         properties["xgboost_model_PATH"] = args.path + "/checkpoint/" + "model_xgboost.pkl"
#         joblib.dump(xgb_best, properties["xgboost_model_PATH"])
#         logger.info("手动调参模型成功保存")
#     elif auto_value==int(1):
#         logger = properties["LOGGER"]
#         logger.info("自动调参模型开始训练")
#         param_max_depth = {'max_depth': [5,7,9]}
#         param_min_child_weight = {'min_child_weight': [3,9,15]}
#         param_n_estimators = {'n_estimators': [50,100,200,400]}
#         param_gamma = {'gamma': [0, 0.1,0.2]}
#         param_learning_rate = {'learning_rate': [0.1, 0.2, 0.3]}
#         param_subsample = {'subsample': [ 0.8, 0.9, 0.95]}
#         param_colsample_bytree = {'colsample_bytree': [0.8, 0.9, 0.95]}
#         ##param_max_depth调参
#         param_grid_list = [param_max_depth, param_min_child_weight, param_n_estimators,
#                            param_gamma, param_learning_rate, param_subsample, param_colsample_bytree]
#         param_name = ["max_depth", "min_child_weight", "n_estimators",
#                       "gamma", "learning_rate", "subsample", "colsample_bytree"]
#         param_num = len(param_name)
#
#         estimator_xgb_adj = XGBClassifier(max_depth=6,
#                                           min_child_weight=5,
#                                           n_estimators=200,
#                                           gamma=0,
#                                           learning_rate=0.1,
#                                           subsample=0.8,
#                                           colsample_bytree=0.8,
#                                           objectiv='binary:logistic',
#                                           scale_pos_weight=bili,
#                                           seed=27)
#         params_best = []
#         for i in range(param_num):
#             gsearch_xgboost = GridSearchCV(estimator=estimator_xgb_adj,
#                                            param_grid=param_grid_list[i],
#                                            scoring='roc_auc',
#                                            iid=False,
#                                            cv=3)
#             gsearch_xgboost.fit(x_train, y_train)
#             param_best = gsearch_xgboost.best_params_[param_name[i]]
#             params_best.append(param_best)
#         status = properties['STATUS']
#         status.heartbeat(str(properties["FILE_PREFIX"]), "60%")
#
#         xgb_best = XGBClassifier(max_depth=params_best[0],
#                                  min_child_weight=params_best[1],
#                                  n_estimators=params_best[2],
#                                  gamma=params_best[3],
#                                  learning_rate=params_best[4],
#                                  subsample=params_best[5],
#                                  colsample_bytree=params_best[6],
#                                  objectiv='binary:logistic',
#                                  scale_pos_weight=bili,
#                                  seed=27)
#
#         xgb_best.fit(x_train, y_train)
#         # 存储xgboost模型
#         properties["xgboost_model_PATH"] = args.path + "/checkpoint/" + "model_xgboost.pkl"
#         joblib.dump(xgb_best, properties["xgboost_model_PATH"])
#         logger.info("自动模型成功保存")
#
#     status = properties['STATUS']
#     status.heartbeat(str(properties["FILE_PREFIX"]), "70%")
#
#     y_pre_train = xgb_best.predict(x_train)
#     y_true_train = y_train
#     C_train = confusion_matrix(y_true_train, y_pre_train)
#     accury_train = (C_train[0, 0] + C_train[1, 1]) / (C_train[0, 0] + C_train[0, 1] + C_train[1, 0] + C_train[1, 1])
#     accury_train = '%.2f' % accury_train
#     recall_train = C_train[1, 1] / (C_train[1, 0] + C_train[1, 1])
#     recall_train = '%.2f' % recall_train
#     Precison_train = C_train[1, 1] / (C_train[0, 1] + C_train[1, 1])
#     Precison_train = '%.2f' % Precison_train
#
#
#     y_pre_test = xgb_best.predict(x_test)
#     y_true_test = y_test
#     C_test = confusion_matrix(y_true_test, y_pre_test)
#
#     status = properties['STATUS']
#     status.heartbeat(str(properties["FILE_PREFIX"]), "80%")
#     accury_test = (C_test[0, 0] + C_test[1, 1]) / (C_test[0, 0] + C_test[0, 1] + C_test[1, 0] + C_test[1, 1])
#     accury_test = '%.2f' % accury_test
#     recall_test = C_test[1, 1] / (C_test[1, 0] + C_test[1, 1])
#     recall_test = '%.2f' % recall_test
#     Precison_test = C_test[1, 1] / (C_test[0, 1] + C_test[1, 1])
#     Precison_test = '%.2f' % Precison_test
#
#     train_pinggu = "training_outputs=产品:分类,操作:训练,精度:%s,召回率:%s,查准率:%s" % (accury_train, recall_train,Precison_train)
#     test_pinggu = "testing_outputs=产品:分类,操作:测试,精度:%s,召回率:%s,查准率:%s" % (accury_test, recall_test,Precison_test)
#
#
#     result_sum = [train_pinggu, test_pinggu]
#     result_sum_str = ""
#     for yuansu in result_sum:
#         #
#         result_sum_str = result_sum_str + yuansu + "\n"
#     status = properties['STATUS']
#     status.heartbeat(str(properties["FILE_PREFIX"]), "90%")
#
#     # result_sum_str = result_sum_str.strip("#")
#     logger.info("模型训练结束")
#     status = properties['STATUS']
#     status.heartbeat(str(properties["FILE_PREFIX"]), "100%")
#     return result_sum_str
#

from xgboost.sklearn import XGBClassifier
from carport.data import dbutil as db
from carport.train_predict.data_generate import *
from carport.train_predict.data_pro import *
from sklearn.metrics import confusion_matrix
from sklearn.externals import joblib



path_model_dir = "C:/Users/wangquan/Desktop/xgboost/model/"
path_log = "C:/Users/wangquan/Desktop/xgboost/log/log.txt"

chepai_dic = db.queryCarsInfo()
dataframe_list = data_gr(chepai_dic)

def train_xgboost(data,chepai_name,path_model_dir):
    x_train_list, x_test_list, y_train_list, y_test_list = train_data_main(data)
    nn =[]
    if len(x_train_list) < 24:
        cont = chepai_name + "数据存在问题，没有24个小时的数据，因此无法建模"
        with open(path_log, "a") as reader:
            reader.write(cont + "\n")
        nn.append(chepai_name)
    else:
        cont = chepai_name + "数据不存在问题，有24个小时的数据，可以建模"
        with open(path_log, "a") as reader:
            reader.write(cont + "\n")
        s0_0_test = []
        s0_1_test = []
        s1_0_test = []
        s1_1_test = []
        for j in range(24):
            x_train = x_train_list[j]
            y_train = y_train_list[j]
            x_test = x_test_list[j]
            y_test = y_test_list[j]
            bili = (len(y_train) - sum(y_train)) / sum(y_train)

            model = XGBClassifier(max_depth=6,
                                  min_child_weight=4,
                                  n_estimators=200,
                                  gamma=0,
                                  learning_rate=0.3,
                                  subsample=0.9,
                                  colsample_bytree=0.9,
                                  scale_pos_weight=bili,
                                  objective='binary:logistic')
            model.fit(x_train, y_train)
            model_path = path_model_dir + chepai_name + "_" + str(j) + "_model.m"




            joblib.dump(model, model_path)
            y_pre_test = model.predict(x_test)
            y_true_test = y_test
            C_test = confusion_matrix(y_true_test, y_pre_test)
            s0_0_test.append(C_test[0, 0])
            s0_1_test.append(C_test[0, 1])
            s1_0_test.append(C_test[1, 0])
            s1_1_test.append(C_test[1, 1])
        recall_value_mean = sum(s0_0_test) / (sum(s0_0_test) + sum(s0_1_test))
        cont = chepai_name + "业主的召回率为：" + str(round(recall_value_mean, 2))
        with open(path_log, "a") as reader:
            reader.write(cont + "\n")
    return nn

def trains_xgboost(dataframe_list,path_model_dir,path_log):
    dataframe_num = len(dataframe_list)
    names_not_inuse = []
    for i in range(dataframe_num):
        data = dataframe_list[i]
        chepai_name = list(data["车牌号"])[0]
        if len(data)<=80:
            cont = chepai_name + "原始数据样本量少于80，不符合建模条件，因此抱歉不能建模"
            with open(path_log, "a") as reader:
                reader.write(cont + "\n")
            names_not_inuse.append(chepai_name)
        else:
            cont = chepai_name + "原始数据样本量大于80，初步符合建模条件，因此继续进行数据处理"
            with open(path_log, "a") as reader:
                reader.write(cont + "\n")
            nn = train_xgboost(data, chepai_name, path_model_dir)
            if len(nn)==0:
                pass
            else:
                names_not_inuse.append(nn[0])
    names_inuse_path = path_model_dir + "names_not_inuse.m"
    joblib.dump(names_not_inuse, names_inuse_path)


if __name__ == "__main__":
    trains_xgboost(dataframe_list, path_model_dir, path_log)






































