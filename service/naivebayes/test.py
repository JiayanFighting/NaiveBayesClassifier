#!/usr/bin/python
# coding=utf-8

import math
import json
from sklearn.naive_bayes import MultinomialNB
from sklearn.externals import joblib
from service.utils.AttributeFeatureUtil import AttributeFeatureUtil
from service.utils.TextFeatureUtil import TextFeatureUtil
import pymysql.cursors
import io
import sys
print(sys.path)

# mysql init
def get_cursor():
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='710315huang',
                                 db='comment_system',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection.cursor()

#获取用户信息
def getUserInfo(userid):
    cursor = get_cursor()
    cursor.execute("select * from userinfo where userid="+userid)
    result = cursor.fetchall()
    friend_num = 0
    for row in result:
        friend_num = row["friend_num"]
    return friend_num

