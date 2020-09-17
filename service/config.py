#!/usr/bin/python
#--coding=utf8
# -*- coding: utf-8 -*- 
import sys,logging, logging.handlers


class ServiceConfig():
    logpath = "web_service.log"


#设置默认logger
logging.getLogger("").setLevel(logging.WARN)

# 创建logger
def get_logger(tag="HTTP"):
    logger = logging.getLogger(tag)
    fh = logging.handlers.TimedRotatingFileHandler(ServiceConfig.logpath, when='D')
    fh.suffix = '%Y-%m-%d.%H'
    formatter = logging.Formatter('%(asctime)s - %(name)s -[%(levelname)s]  %(message)s')
    fh.setFormatter(formatter)
    # 再创建一个handler，用于输出到控制台
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARN)
    ch.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)
    logger.setLevel(logging.DEBUG)
    return logger

