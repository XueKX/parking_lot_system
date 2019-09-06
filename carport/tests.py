# from django.test import TestCase

# Create your tests here.
# table = {1:2, 5:5, 24:10}
# for i in table:
# 	print(i)

import time,datetime



def print_timestamp(timestamp):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp/1000))



list=[1,2,3,4,5]
list.remove(3)
print(list)

