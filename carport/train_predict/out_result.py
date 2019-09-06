import pandas as pd
import os
import sqlite3

path_yuce_dir = "../../codedir/ensemble/"
database_path = './db.sqlite3'


def out_results(path_yuce_dir):
    file_names = os.listdir(path_yuce_dir)
    file_names_path = [path_yuce_dir + file_name for file_name in file_names]
    data_llist = []
    for path in file_names_path:
        data = pd.read_csv(path, encoding="utf-8", engine="python", names=["车牌号", "概率"])
        data = data.drop([0], axis=0)
        data = data.reset_index(drop=True)

        column_names = []
        for i in range(24):
            column_name = str(i) + "-" + str(i + 1)
            column_names.append(column_name)

        gailv = list(data["概率"])
        data_dir = {"car_license": [data["车牌号"][0]]}

        for i in range(24):
            data_dir[column_names[i]] = [round(gailv[i], 2)]
        data_trans = pd.DataFrame(data_dir)
        data_llist.append(data_trans)
    data_all = pd.concat(data_llist, axis=0)
    return data_all


def filter_results(df, start, end):
    '''
    Return information about free parking Spaces
    :param df:
    :param start:start time of parking
    :param end:end time of parking
    :return:
    '''
    duration = str(start) + '-' + str(end)
    start = str(start) + '-' + str(start + 1)
    end = str(end - 1) + '-' + str(end)
    con = sqlite3.connect(database_path)
    pd.io.sql.to_sql(df, 'carport_logs', con=con, if_exists='replace')

    start_index = list(df.columns).index(start)
    end_index = list(df.columns).index(end)
    for i in range(start_index, end_index + 1):
        key = list(df.columns)[i]
        df = df[df[key] > 0.5]
    sum = 0
    for i in range(start_index, end_index + 1):
        key = list(df.columns)[i]
        sum += df[key]
    df['result'] = (sum / (end_index - start_index + 1)).sort_values(ascending=False)
    car_license = df.iloc[:, 0].tolist()
    free_prob_list = df.iloc[:, -1].tolist()
    if len(car_license) > 20:
        car_license = car_license[0:20]
        free_prob_list = free_prob_list[0:20]
    dic = dict(zip(car_license, free_prob_list))
    # print(df, dic)
    return query(con, car_license, dic, duration)


def query(con, car_license, dic, duration):
    '''
    Return information about free parking Spaces
    :param con:
    :param car_license:
    :param dic:
    :return:
    '''
    c = con.cursor()
    results = []
    for i, license in enumerate(car_license):
        cursor = c.execute("SELECT * from carport_link WHERE car_license='{}'".format(license))
        for row in cursor:
            rows = list(row)
            rows.append(dic[license])
            rows.append(duration)
            del rows[0]
            # print(rows)
            results.append(rows)
    con.close()
    print(results)
    return results


if __name__ == "__main__":
    data_all = out_results(path_yuce_dir)

    start = 10
    end = 18
    results = filter_results(data_all, start, end)
