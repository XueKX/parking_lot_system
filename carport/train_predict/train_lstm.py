
from carport.data import dbutil as db
from carport.train_predict.data_generate import *
from carport.train_predict.data_pro import *
from keras.models import Sequential
from keras.layers import Dense
from keras.utils import plot_model
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation
from keras.layers.embeddings import Embedding
from sklearn.metrics import confusion_matrix
from sklearn.externals import joblib
from keras.backend import clear_session

path_model_dir = "C:/Users/wangquan/Desktop/lstm/model/"
path_log = "C:/Users/wangquan/Desktop/lstm/log/log.txt"


chepai_dic = db.queryCarsInfo()
dataframe_list = data_gr(chepai_dic)

def train_lstm(data,chepai_name,path_model_dir):
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
            model = Sequential()
            model.add(Dense(32, input_dim=168, activation='relu'))
            model.add(Dense(1))
            model.compile(loss='binary_crossentropy', optimizer='adam')
            model.fit(x_train, y_train, epochs=50, batch_size=64, verbose=2)

            model_path = path_model_dir + chepai_name + "_" + str(j) + "_model.m"
            joblib.dump(model, model_path)

            y_pre = model.predict(x_test)
            y_pre = y_pre.reshape(len(y_pre),)
            y_pre_test = np.where(y_pre >= 0.5, 1, 0)
            y_true_test = y_test
            C_test = confusion_matrix(y_true_test, y_pre_test)
            s0_0_test.append(C_test[0, 0])
            s0_1_test.append(C_test[0, 1])
            s1_0_test.append(C_test[1, 0])
            s1_1_test.append(C_test[1, 1])
            clear_session()
        recall_value_mean = sum(s0_0_test) / (sum(s0_0_test) + sum(s0_1_test))
        cont = chepai_name + "业主的召回率为：" + str(round(recall_value_mean, 2))
        with open(path_log, "a") as reader:
            reader.write(cont + "\n")

    return nn




def trains_lstm(dataframe_list,path_model_dir,path_log):
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
            nn = train_lstm(data, chepai_name, path_model_dir)
            if len(nn)==0:
                pass
            else:
                names_not_inuse.append(nn[0])
    names_inuse_path = path_model_dir + "names_not_inuse.m"
    joblib.dump(names_not_inuse, names_inuse_path)


if __name__ == "__main__":
    trains_lstm(dataframe_list, path_model_dir, path_log)
















































