#!/usr/bin/python
# coding=utf-8
import math
import json
import time
from service.utils.AttributeFeatureUtil import AttributeFeatureUtil
from service.utils.TextFeatureUtil import TextFeatureUtil
from service.naivebayes.NaiveBayes import NaiveBayesClassifier
from service.naivebayes.NaiveBayes import Feature
import pymysql.cursors
import sys
reload(sys)
sys.setdefaultencoding('utf8')

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
    if len(result) == 0:
        print "user does not exist ！ "
        exit()
    userinfo = {}
    for row in result:
        userinfo['userid'] = row['userid']
        userinfo['nickname'] = row['nickname']
        userinfo['registertime'] = row['registertime']
        userinfo['type'] = row['type']
        userinfo['friend_num'] = row['friend_num']
        userinfo['fan_num'] = row['fan_num']
        userinfo['richlevel'] = row['richlevel']
        userinfo['starlevel'] = row['starlevel']
    return userinfo

# 用户信息处理
def firstStep():
    userid = raw_input("Enter userid: ");
    print "=============================="
    if userid.isdigit():
        print "Received userid is : ", userid
    else:
        print "input wrong!"
        exit()
    print "=============================="
    userinfo = getUserInfo(userid)
    # userinfo['nickname'] = u"哈尼维维😊"
    print "Received userinfo is : "
    print "userid       : ", userinfo['userid']
    print "nickname     : ", userinfo['nickname']
    print "registertime : ", userinfo['registertime']
    print "type         : ", userinfo['type']
    print "friend_num   : ", userinfo['friend_num']
    print "fan_num      : ", userinfo['fan_num']
    print "richlevel    : ", userinfo['richlevel']
    print "starlevel    : ", userinfo['starlevel']
    print "=============================="
    print "Processed userinfo is : "
    fieldnames = ['id'.decode("utf-8"), 'nickname'.decode("utf-8"), 'registertime'.decode("utf-8"),
                  'type'.decode("utf-8"), 'friend_num'.decode("utf-8"), 'fan_num'.decode("utf-8"),
                  'richlevel'.decode("utf-8"), 'starlevel'.decode("utf-8")]
    registertime = userinfo['registertime'].strftime("%Y-%m-%d %H:%M:%S").decode("utf-8")
    userFeature = [
        userinfo['userid'], userinfo['nickname'], registertime, userinfo['type'], userinfo['friend_num'],
        userinfo['fan_num'], userinfo['richlevel'], userinfo['starlevel']
    ]
    AttributeFeatureUtil.preprocessData(fieldnames, userFeature)
    print "userid       : ", userFeature[0]
    print "nickname     : ", userFeature[1]
    print "registertime : ", userFeature[2]
    print "type         : ", userFeature[3]
    print "friend_num   : ", userFeature[4]
    print "fan_num      : ", userFeature[5]
    print "richlevel    : ", userFeature[6]
    print "starlevel    : ", userFeature[7]
    print "=============================="
    print "=============================="
    return userFeature

# 文本处理
def secondStep(userid):
    text = raw_input("Enter comment: ")
    print "=============================="
    print "Received comment is  : ", text
    text = text.decode("utf-8")
    ret = TextFeatureUtil.getText(userid,text, 1)
    if ret == 1:
        print "无效文本 -- 评论长度不达标"
        exit()
    elif ret == 2:
        print "无效文本 -- 过滤符号表情后评论长度不达标"
        exit()
    else:
        print "Processed comment is : ",ret['text']
    print "=============================="
    return ret['text']


# 构造特征向量
def thirdStep(userFeature,text):
    return Feature(userFeature, text)

# 分类
def fourthStep(testFeature):
    nbClassifier = NaiveBayesClassifier()
    nbClassifier.loadModel("../../resource/model")
    text = testFeature.textFeature
    vocabList = nbClassifier.vocabList
    print "=============================="
    flag = 0


    if TextFeatureUtil.isAllStopWords(vocabList, text) == True:
        print "\033[1;35m All are isAllStopWords ! \033[0m"
        flag = 1
    t1 = time.time()
    t1 = (int(round(t1 * 1000)))
    # print "开始:", t1  # 毫秒级时间戳
    result = nbClassifier.predict(testFeature)
    t2 = time.time()
    t2 = (int(round(t2 * 1000)))
    # print "结束：", t2  # 毫秒级时间戳

    if result and flag == 0 :
        print "\033[1;35m it's bad comment! \033[0m"
        # print(testFeature.textFeature)
        flag = 1
    if flag == 0:
        negativewords = nbClassifier.getNegativeWordsList()
        for word in negativewords:
            if text.find(word) != -1:
                # print "\033[1;35m include negative word :", word,"\033[0m"
                # print(testFeature.textFeature)
                print "\033[1;35m it's bad comment! \033[0m"
                flag = 1
                break
    if flag == 0:
        print "\033[1;35m it's normal comment!\033[0m"

    print "=============================="
    print "耗时:", t2 - t1, " ms"

def main():
    print 1
    # 用户信息处理
    userFeature = firstStep()
    print 2
    # 文本处理
    text = secondStep(userFeature[0])
    print 3
    # 构造特征向量
    feature = thirdStep(userFeature, text)
    print 4
    # 分类
    fourthStep(feature)

main()