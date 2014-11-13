#coding=utf-8
#

import logging

file = "../logs/webpy.log" # 日志文件路径 #
logformat = "[%(asctime)s] %(filename)s:%(lineno)d: [%(levelname)s] %(message)s" # 日志格式 #
#logformat = "[%(asctime)s] %(filename)s:%(lineno)d(%(funcName)s): [%(levelname)s] %(message)s" # 日志格式 #
datefmt = "%Y-%m-%d %H:%M:%S" # 日志中显示的时间格式 #
loglevel = logging.DEBUG
interval = "d" # 每隔一天生成一个日志文件#
backups = 365 # 后台保留3个日志文件 #

train_spam_path = '../data/untrain_spam.txt'
train_ham_path = '../data/untrain_ham.txt'
vocabulary_path = '../data/vocab.txt'
spam_path = '../data/spam.txt'
ham_path = '../data/ham.txt'




