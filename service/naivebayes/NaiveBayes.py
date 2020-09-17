#!/usr/bin/python
# coding=utf-8

import math
import json
import time
from sklearn.naive_bayes import MultinomialNB
from sklearn.externals import joblib
from service.utils.AttributeFeatureUtil import AttributeFeatureUtil
from service.utils.TextFeatureUtil import TextFeatureUtil
# import pymysql.cursors
import io
import sys
reload(sys)
sys.setdefaultencoding('utf8')

# 特征类
class Feature:

    # 属性特征+文本特征
    def __init__(self, attributeFeature, textFeature):
        self.attributeFeature = attributeFeature
        self.textFeature = textFeature


# 朴素贝叶斯分类器
class NaiveBayesClassifier:

    def __init__(self):
        self.fieldNames = ['id', 'nickname', 'registertime', 'type', 'friend_num', 'fan_num','richlevel','starlevel']
        self.fieldValues = self.getFieldnameValues()
        self.vocabList = None
        self.mnb = None

    # 获取特征集合
    def getTestFeatures(self, userInfoFile, textFile):
        t11 = time.time()
        t11 = (int(round(t11 * 1000)))
        normalTextFeatures = TextFeatureUtil.getTextList(textFile, 1)
        t22 = time.time()
        t22 = (int(round(t22 * 1000)))
        userList = AttributeFeatureUtil.getUserFeature([userInfoFile])
        t33 = time.time()
        t33 = (int(round(t33 * 1000)))
        print "处理文本耗时",t22-t11,"ms"
        print "处理用户特征耗时", t33 - t22, "ms"
        testFeatures = []
        for i in range(len(normalTextFeatures)):
            userid = normalTextFeatures[i]['userid']
            if userList.__contains__(userid):
                userFeature = userList[userid]
                text = normalTextFeatures[i]['text']
                testFeature = Feature(userFeature, text)
                testFeatures.append(testFeature)
        t44 = time.time()
        t44 = (int(round(t44 * 1000)))
        print "构建特征耗时", t44 - t33, "ms"
        return testFeatures

    # 获取属性的取值列表
    def getFieldnameValues(self):
        # 属性对应的取值集合
        fieldname_values = {}
        for i in range(len(self.fieldNames)):
            fieldname = self.fieldNames[i]
            # id 列直接跳过
            if fieldname == "id":
                continue
            else:
                # 获取属性对应的值列表
                values = AttributeFeatureUtil.getValues(fieldname)
                fieldname_values[fieldname] = values
        return fieldname_values

    # 产生特征向量集合
    def generateVectors(self, features):
        vectors = []
        for feature in features:
            vector = self.generateVector(feature)
            if vector == -1:
                continue
            vectors.append(vector)
        return vectors

    # 产生特征向量
    def generateVector(self, feature):
        vector = []
        textFeature = feature.textFeature
        attributeFeature = feature.attributeFeature
        textVector = self.generateTextVector(textFeature)
        if textVector == -1:
            return -1
        attributeVector = self.generateAttributeVector(attributeFeature)
        vector.extend(textVector)
        vector.extend(attributeVector)
        return vector

    # 产生文本特征向量
    def generateTextVector(self, textFeature):
        vocabList = self.vocabList
        textVector = TextFeatureUtil.getTextVector(vocabList, textFeature)
        if textVector == -1:
            return -1
        textLength = len(textFeature)
        textLength = int(round(math.log(textLength,2)))
        textLength = min(textLength, 8)
        textLengthVector = [0] * 9
        textLengthVector[textLength] = 1
        textVector.extend(textLengthVector)
        return textVector

    # 产生属性特征向量
    def generateAttributeVector(self, attributeFeature):
        data_vector = []
        for i in range(len(self.fieldNames)):
            fieldname = self.fieldNames[i]
            if fieldname == "id":
                continue
            value = attributeFeature[i]
            # attributeFeature
            values = self.fieldValues[fieldname]
            if not isinstance(values[0], str):
                value = int(value)
            index = values.index(value)
            field_vector = [0] * len(values)
            field_vector[index] = 1
            data_vector.extend(field_vector)
        return data_vector

    def NaiveBayes(trainVectors, trainResults):
        pos_pn = [0,0]
        pos_total_0 =[]
        pos_total_1 = []
        for i in range(len(trainResults)) :
            if trainResults[i] == 0:
                pos_pn[0] = pos_pn[0] + 1
            else:
                pos_pn[1] = pos_pn[1] + 1
        vec_0 = []
        vertor = trainVectors[0]
        vec_len = len(vertor)
        for j in range(vec_len):
            count_vec_0 = {}
            count_vec_1 = {}
            total_0 = 0
            total_1 = 0
            for i in range(len(trainVectors)):
                vertor = trainVectors[i]
                value = vertor[j]
                if trainResults[i] == 0:
                    num = count_vec_0.get(value,0)
                    num = num + 1
                    count_vec_0[value] = num
                    total_0 = total_0 + 1
                else:
                    num = count_vec_1.get(value, 0)
                    num = num + 1
                    count_vec_1[value] = num
                    total_1 = total_1 + 1
            pos_vec_0 = {}
            for key, value in count_vec_0.items():
                pos_vec_0[key] = count_vec_0[key] / total_0
            pos_vec_1 = {}
            for key, value in count_vec_1.items():
                pos_vec_1[key] = count_vec_1[key] / total_1
            pos_total_0[j] = pos_vec_0
            pos_total_1[j] = pos_vec_1
        return [pos_total_0,pos_total_1]

    # 训练模型
    # 1.正样本文件列表 2.负样本文件列表
    def trainModel(self, normalUserInfo,normalComment,badUserInfo,badComment):
        # 载入数据
        # 1.文本数据处理
        t1 = (int(round(time.time() * 1000)))
        normalTextFeatures = TextFeatureUtil.getTextList(normalComment, 1)
        print len(normalTextFeatures)
        badTextFeatures = TextFeatureUtil.getTextList(badComment, 0)
        print len(badTextFeatures)
        textFeatures = normalTextFeatures + badTextFeatures
        print len(textFeatures)
        t2 = (int(round(time.time() * 1000)))
        print "文本处理总耗时：", (t2 - t1) , "ms"

        # 2.用户属性数据处理
        userList = AttributeFeatureUtil.getUserFeature([normalUserInfo,badUserInfo])

        t3 = (int(round(time.time() * 1000)))
        print "用户特征处理总耗时：", (t3 - t2) , "ms"

        # 特征集
        trainFeatures = []
        # 所有评论文本集合，用来构造词典
        trainTexts = []
        # 结果集
        trainResults = []
        # 合并属性特征和文本特征得到特征集合
        for i in range(len(textFeatures)):
            userid = textFeatures[i]['userid']
            if userList.__contains__(userid):
                userFeature = userList[userid]
                text = textFeatures[i]['text']
                trainFeature = Feature(userFeature, text)
                trainFeatures.append(trainFeature)
                trainTexts.append(text)
                trainResults.append(textFeatures[i]['mark'])

        t4 = (int(round(time.time() * 1000)))
        print "构建特征向量耗时：", (t4 - t3) , "ms"
        # 构建词典
        self.vocabList = TextFeatureUtil.constrcutVocabList(trainTexts)
        t5 = (int(round(time.time() * 1000)))
        print "构建词典耗时：", (t5 - t4) , "ms"
        print(len(self.vocabList))
        # 构建训练向量
        trainVectors = self.generateVectors(trainFeatures)
        # 使用分类器进行训练
        mnb = MultinomialNB()
        mnb.fit(trainVectors, trainResults)
        self.mnb = mnb
        t6 = (int(round(time.time() * 1000)))
        print "训练耗时：", (t6 - t5) , "ms"

    # 持久化模型
    def persistModel(self, url):
        joblib.dump(self.mnb, url + '/multinomialNB2')
        vocanList=json.dumps(self.vocabList).decode("utf-8")
        with io.open(url + '/vocabList.json', 'w', encoding="utf-8") as json_file:
            json_file.write(vocanList)

    # 载入模型
    def loadModel(self, url):
        mnb = joblib.load(url + '/multinomialNB2')
        self.mnb = mnb
        with io.open(url + '/vocabList.json', "r", encoding="utf-8") as json_file:
            self.vocabList = json.load(json_file)

    # 针对单条特征做预测
    # 1.True代表有问题 2.False是没问题
    def predict(self, test_feature):
        vector = self.generateVector(test_feature)
        if vector == -1:
            return False
        predict_result = self.mnb.predict([vector])
        if predict_result[0] == 0:
            return True
        else:
            return False

    # 新词挖掘的禁用词
    def getNegativeWordsList(self):
        list = []
        filename = '../utils/negativewords.txt'
        fo = io.open(filename, "r",encoding='utf-8')
        lines = fo.readlines()
        for line in lines:
            line = line.decode("utf-8")
            line = line.strip('\n')
            if (len(line) > 0) :
                list.append(line)
        return list


# 主函数
def main():
    # 训练模型部分
    normalUserInfo = '../../resource/traindata/normal_userinfo_v1.csv'
    normalComment = '../../resource/traindata/normal_comment_v1.txt'
    badUserInfo = '../../resource/traindata/bad_userinfo_v1.csv'
    badComment = '../../resource/traindata/bad_comment_v1.txt'

    # 1.初始化贝叶斯分类器
    nbClassifier = NaiveBayesClassifier()
    # # # # 2.持久化模型
    t1 = (int(round(time.time() * 1000)))
    nbClassifier.trainModel(normalUserInfo,normalComment,badUserInfo,badComment)
    t2 = (int(round(time.time() * 1000)))
    nbClassifier.persistModel("../../resource/model")
    t3 = (int(round(time.time() * 1000)))
    print "训练模型耗时：", (t2 - t1) , "ms"
    print "持久化模型耗时：", (t3 - t2), "ms"
    print "训练模型总耗时：",(t3 - t1),"ms"
    print "训练完毕"

    # 实践部分
    nbClassifier = NaiveBayesClassifier()
    nbClassifier.loadModel("../../resource/model")
    print(len(nbClassifier.vocabList))
    # # 2.做预测
    out = io.open('result2.txt', 'w',encoding='utf-8')
    # # # 3.获取测试集特征集合
    userInfoFile = "../../resource/testdata/userinfo.csv"
    textFile = "../../resource/testdata/comments.txt"
    # userInfoFile = "../../resource/traindata/bad_userinfo_v1.csv"
    # textFile = "../../resource/traindata/bad_comment_v1.txt"
    negativewords = nbClassifier.getNegativeWordsList()
    t1 = time.time()
    t1 = (int(round(t1 * 1000)))
    testFeatures = nbClassifier.getTestFeatures(userInfoFile, textFile)
    t2 = time.time()
    t2 = (int(round(t2 * 1000)))
    print "特征处理完毕，耗时：",t2-t1,"ms"
    for testFeature in testFeatures:
        text = testFeature.textFeature
        vocabList = nbClassifier.vocabList
        if TextFeatureUtil.isAllStopWords(vocabList,text) == True:
            continue
        flag = 0
        result = nbClassifier.predict(testFeature)
        if result:
            print testFeature.attributeFeature[0]
            print(testFeature.textFeature)
            userid = str(testFeature.attributeFeature[0])
            out.write(userid + ":" + testFeature.textFeature + "\n")
            flag = 1
        if flag == 0:
            for word in negativewords:
                if text.find(word) != -1:
                    # print "包含negativeword"
                    print testFeature.attributeFeature[0]
                    print(testFeature.textFeature)
                    userid = str(testFeature.attributeFeature[0])
                    out.write(userid + ":" + testFeature.textFeature + "\n")
                    break
    t3 = (int(round(time.time() * 1000)))
    print "分类",len(testFeatures),"条文本，耗时",t3-t2,"ms"
    out.close()


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


# # 用户信息处理
# userFeature = firstStep()
# # 文本处理
# text = secondStep(userFeature[0])
# # 构造特征向量
# feature = thirdStep(userFeature,text)
# # 分类
# fourthStep(feature)

main()
