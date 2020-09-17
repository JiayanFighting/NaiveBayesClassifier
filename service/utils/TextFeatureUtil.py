#!/usr/bin/python
# coding=utf-8
import re
from enum import Enum
import io
import sys

reload(sys)
sys.setdefaultencoding('utf8')


# 字符类型
class CharType(Enum):
    chinese = 1
    number = 2
    english = 3


def strToUnicode(value):
    return value.decode("utf-8")


# 文本特征处理工具类
class TextFeatureUtil:

    # 构建词向量
    @staticmethod
    def getTextVector(vocabList, text):
        returnVec = [0] * len(vocabList)
        text = TextFeatureUtil.cleanText(text)
        wordSet = TextFeatureUtil.splitText(text)
        flag = 0
        for word in wordSet:
            if word in vocabList:
                returnVec[vocabList.get(word)] = 1
                flag = 1
        # if flag == 0:
        #     return -1
        return returnVec

    @staticmethod
    def isAllStopWords(vocabList, text):
        text = TextFeatureUtil.cleanText(text)
        wordSet = TextFeatureUtil.splitText(text)
        flag = 1
        for word in wordSet:
            if word in vocabList:
                flag = 0
        if flag == 1:
            return True
        return False

    # 得到停用词列表
    @staticmethod
    def getStopWords(filename):
        fo = io.open(filename, "r", encoding="utf-8")
        stopwords = set()
        stopwords.add(" ")

        while True:
            line = fo.readline()
            line = line.decode("utf-8")
            if not line:
                break
            stopword = line.replace("\n", "")
            stopwords.add(stopword)

        fo.close()

        return stopwords

    # 构建词袋
    @staticmethod
    def constrcutVocabList(texts):
        stopwords = TextFeatureUtil.getStopWords("../utils/stopwords.txt")
        stopwords.add("\n")
        stopwords.add(":")
        words = set()
        for text in texts:
            for word in TextFeatureUtil.splitText(text):
                if word not in stopwords and len(word.strip())!=0:
                    words.add(word)
            # words = words.union(TextFeatureUtil.splitText(text) - stopwords)
        words = list(words)
        words.sort
        vocabList = {}
        index = 0
        for word in words:
            vocabList[word] = index
            index += 1
        return vocabList

    # 输出字符的类型
    @staticmethod
    def getCharType(ch):
        ch = ch.lower()
        if u'\u4e00' <= ch <= u'\u9fff':
            return CharType.chinese
        elif '0' <= ch <= '9':
            return CharType.number
        elif 'a' <= ch <= 'z':
            return CharType.english

    # 拆分文本从而得到词
    # 1.汉字单字 2.数字连续组合 3.字符连续组合
    @staticmethod
    def splitText(text):

        words = set()
        lastType = CharType.chinese
        lastIndex = 0

        for i in range(len(text)):
            ch = text[i]
            currentType = TextFeatureUtil.getCharType(ch)
            if (currentType == CharType.chinese):
                words.add(strToUnicode(str(ch)))
            if (currentType != lastType):
                # 上一个字符不是中文需要添加
                if (lastType != CharType.chinese):
                    words.add(strToUnicode(text[lastIndex:i]))
                lastType = currentType
                lastIndex = i
            # 最后一个字符的话
            if ((i + 1) >= len(text) and currentType != CharType.chinese):
                words.add(strToUnicode(text[lastIndex:]))

        return words

    # 利用正则表达式过滤无效文本，只保留数字+汉字+英文+常用特殊字符，其他全部去掉
    @staticmethod
    def cleanText(text):
        cop = re.compile(u"[^\u4e00-\u9fa5^\s^a-z^A-Z^0-9]")
        return cop.sub("", text)

    # 读出多行文本,只是进行了最基本的过滤操作
    @staticmethod
    def getTexts(filename):
        fo = io.open(filename, "r", encoding='utf-8')
        lines = fo.readlines()
        texts = []
        for line in lines:
            line = line.decode("utf-8")
            strs = line.split(":")
            if len(strs) < 2:
                continue
            else:
                text = line[len(strs[0]) + 1:]
                text = TextFeatureUtil.cleanText(text)
                texts.append(text)
        return texts

    # 判断是否是无效文本，系统产生视为无效
    @staticmethod
    def isInvalidText(text):
        filterStrs = ['来听听我唱', 'gif', '击败', '转发', '打败']
        for filterStr in filterStrs:
            if text.find(filterStr) == -1:
                continue
            return True
        if len(text) <= 3:
            return True
        else:
            return False


    @staticmethod
    def getTextList(filename,mark):
        textList = []
        fo = io.open(filename, "r", encoding='utf-8')
        lines = fo.readlines()
        for line in lines:
            line = line.decode("utf-8")
            strs = line.split(":")
            if len(strs) < 2:
                continue
            userid = int(strs[0])
            text = line[len(strs[0]) + 1:]
            text = text.strip('\n')
            ret = TextFeatureUtil.getText(userid,text,mark)

            if ret == 2 or ret == 1:
                # 没有userid或者text则跳过
                continue
            else:
                textList.append(ret)
        return textList

    @staticmethod
    def getText(userid,text,mark):
        info = {}
        # 评论长度<3的或者包含相关字的为无效文本，跳过
        if TextFeatureUtil.isInvalidText(text):
            return 1
        # 利用正则表达式过滤无效文本，只保留数字+汉字+英文+常用特殊字符，其他全部去掉
        text = TextFeatureUtil.cleanText(text)
        if len(text) == 0:
            return 2
        else:
            info['userid'] = userid
            info['text'] = text
            info['mark'] = mark
            return info


# text="11傻:\n"
# text=text.decode("utf-8")
# text=TextFeatureUtil.cleanText(text)
# # text=text.decode("utf-8")
# print(len(text))
# print(TextFeatureUtil.cleanText(text))
# print(TextFeatureUtil.constrcutVocabList([text]))

