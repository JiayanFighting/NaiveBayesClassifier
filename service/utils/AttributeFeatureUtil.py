#!/usr/bin/python
# coding=utf-8
import os
import pandas as pd
import sys
import time
import math
# import sys
#
# reload(sys)
# sys.setdefaultencoding('utf8')


# 属性特征处理类
class AttributeFeatureUtil:


    # 预处理数据：使得数据在给定的数据空间内,同时对数据进行一定的变换
    @staticmethod
    def preprocessData(fieldnames, parts):
        # 最大值的设定会影响数据的变换
        maxlimit = {'friend_num': 4, 'fan_num': 4}
        numericAttributes = ['friend_num', 'fan_num']
        for i in range(len(fieldnames)):
            # 缺失值类型为nan转为None
            name = fieldnames[i]
            if name == "id":
                continue
            elif name == "nickname":
                parts[i] = AttributeFeatureUtil.getNicknameType(parts[i])
            elif name == "registertime":
                parts[i] = AttributeFeatureUtil.getHour(parts[i])
            elif name == "type":
                parts[i] = AttributeFeatureUtil.getType(parts[i])
            elif name in numericAttributes:
                parts[i] = round(math.log10(parts[i] + 1))
                parts[i] = min(parts[i], maxlimit[name])

    # 获取注册时区
    @staticmethod
    def getHour(registerTime):
        if registerTime == None or registerTime == "":
            return 24
        else:
            registerTime = time.localtime(time.mktime(time.strptime(registerTime, "%Y-%m-%d %H:%M:%S")))
        return registerTime.tm_hour

    # 四种情况：0.纯数字 1.字母+数字 2.包含表情 3.其他类型
    @staticmethod
    def getNicknameType(nickname):
        if nickname==None or nickname=="":
            return 4
        nickname = nickname.lower()
        # 判断是否是纯数字
        flag = True
        for ch in nickname:
            if '0' >= ch or ch >= '9':
                flag = False;
        if flag:
            return 0
        flag = True
        # 判断是否是字母加数字的组合
        for ch in nickname:
            if '0' <= ch <= '9' or 'a' <= ch <= 'z':
                continue
            else:
                flag = False
        if flag:
            return 1;
        # 判断是否包含表情
        for ch in nickname:
            if AttributeFeatureUtil.isEmoji(ch):
                return 2;
        return 3

    # 得到来源
    @staticmethod
    def getType(type):
        if type == None or type == "":
            return "none"
        else:
            return type

    # 是否包含表情
    @staticmethod
    def isEmoji(content):
        if not content:
            return False
        if u"\U0001F600" <= content and content <= u"\U0001F64F":
            return True
        elif u"\U0001F300" <= content and content <= u"\U0001F5FF":
            return True
        elif u"\U0001F680" <= content and content <= u"\U0001F6FF":
            return True
        elif u"\U0001F1E0" <= content and content <= u"\U0001F1FF":
            return True
        else:
            return False

    # 返回一列的取值集合
    @staticmethod
    def getValues(fieldName):
        # 设定属性对应的取值范围
        maxlimit = {'flower_num': 4, 'friend_num': 4, 'fan_num': 4, 'work_num': 3, 'coin_sum': 6, 'coin_buy': 6,
                    'phone': 2, 'registertime': 24, 'coin_buy_ratio': 7, 'richlevel': 27, 'starlevel': 33,
                    'nickname': 4}
        if maxlimit.__contains__(fieldName):
            return list(range(0, maxlimit.get(fieldName) + 1))
        elif fieldName == "type":
            return ['weixin', 'weibo', 'tencent', 'phone', 'renren', "none"]

    # 载入单个数据文件
    @staticmethod
    def getUserFeature(fileList):
        features = []
        fieldnames = []
        userList = {}
        for filename in fileList:
            # 文件是否存在
            # if not os.path.exists(filename):
            #     return (fieldnames, features, results)

            df = pd.read_csv(filename, encoding="utf-8")
            df = df.fillna(
                {'friend_num': 0, 'fan_num': 0, 'nickname': "", "registertime": "", 'richlevel': 0, 'starlevel': 0})
            fieldnames = df.columns.values.tolist()
            features = df.values.tolist()
            for feature in features:
                AttributeFeatureUtil.preprocessData(fieldnames, feature)
                userList[feature[0]] = feature
        return userList


def test():
    fieldnames = ['id', 'nickname', 'registertime', 'type', 'friend_num', 'fan_num']
    feature = [235558915, '入骨情话1314', None, None, 2, 19]
    AttributeFeatureUtil.preprocessData(fieldnames, feature)
    print(feature)
