import sqlite3

def queryCarsInfo():

    conn = sqlite3.connect("G:/wangquan/project_newland/tcw/djproject/carports/db.sqlite3")

    c = conn.cursor()
    print ("Opened database successfully");

    allcars = {}
    cursor = c.execute("select t.car_license, t.begin_time, t.end_time, t.total_time from carport_record t   order by t.car_license , t.begin_time")
    for row in cursor:
       print("ID = ", row[0])
       cartemp = []
       cartemp.append(row[1])
       cartemp.append(row[2])
       cartemp.append(row[3])
       if row[0] in allcars:
           allcars[row[0]].append(cartemp)
       else:
           carstore = []
           carstore.append(cartemp)
           allcars[row[0]] = carstore

    conn.commit()
    conn.close()

    print("end method")
    return allcars

if __name__ == '__main__':
    aa = queryCarsInfo()
    print(aa)