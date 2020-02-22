#!/usr/bin/env python3.5+
# -*- coding: utf-8 -*-
"""
@auth: cml
@date: 2020-2-21
@desc: ...
"""
import logging.config
import os
import sys
curr_path = os.path.abspath(os.path.dirname(__file__))
print(curr_path)
sys.path.append(curr_path)
# from .logger_filters import *
'''
日志的配置参数，日志对象主要有3个子模块，分别为formater（输出格式），handler（日志操作类型），
logger（日志名），要分别进行设置。其中hadlers为日志的具体执行，依赖于formater和日志操作类
型或一些属性，比如按大小分片还是时间分片，是写入还是打印到控制台。
logger负责调用handle，一个logger可以调用多个handler，比如logger.info调用了打印到控制台
handler（logging.StreamHandler）和写入到文件handler（mlogging.TimedRotatingFileHandler_MP），
在没有指定logger名字的时候，即logger=logging.get_logger()的时候，logger会自动选择名为root的logger
'''

# 当前目录
output_path = os.path.join(os.path.dirname(os.path.dirname(curr_path)), 'output')
print('===path', output_path)
log_root_path = os.path.join(output_path, 'logs')
# print("====>", log_root_path)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,  # 不禁用完成配置之前创建的所有日志处理器
    "formatters": {
        "simple": {
            # 简单的输出模式
            'format': '%(asctime)s | %(levelname)s | PID:%(process)d | TID:%(threadName)s | [%(module)s: %(funcName)s] | - %(message)s'
        },
        'standard': {
            # 较为复杂的输出模式，可以进行自定义
            'format': '%(asctime)s | %(levelname)s | PID:%(process)d | TID:%(threadName)s | [%(module)s: %(funcName)s] | - %(message)s'
        },
    },

    # 过滤器
    "filters": {
        'debug_filter': {
            '()': 'logger_filters.DebugFilter'
        },
        'info_filter': {
            '()': 'logger_filters.InfoFilter'
        },
        'warning_filter': {
            '()': 'logger_filters.WarningFilter'
        },
        'error_filter': {
            '()': 'logger_filters.ErrorFilter'
        },
        'critical_filter': {
            '()': 'logger_filters.CriticalFilter'
        },
        'no_debug_filter': {
            '()': 'logger_filters.NoDebugFilter'
        }
    },
    "handlers": {},
    # "handlers": {
    #     # 写入到文件的hanler，写入等级为info，命名为request是为了专门记录一些网络请求日志
    #     "request": {
    #         # 定义写入文件的日志类，此类为按时间分割日志类，还有一些按日志大小分割日志的类等
    #         "class": "logger_handlers.TimedRotatingFileHandlerMP",
    #         # 日志等级
    #         "level": "INFO",
    #         # 日志写入格式，因为要写入到文件后期可能会debug用，所以用了较为详细的standard日志格式
    #         "formatter": "standard",
    #         # 要写入的文件名
    #         "filename": os.path.join(log_root_path, 'default', 'request.log'),
    #         # 分割单位，D日，H小时，M分钟，W星期，一般是以小时或天为单位
    #         # 比如文件名为test.log，到凌晨0点的时候会自动分离出test.log.yyyy-mm-dd
    #         "when": 'D',
    #         "encoding": "utf8",
    #         'backupCount': 5,   # 备份份数
    #     },
    #     # 输出到控制台的handler
    #     "debug": {
    #         # 定义输出流的类
    #         "class": "logging.StreamHandler",
    #         # handler等级，如果实际执行等级高于此等级，则不触发handler
    #         "level": "DEBUG",
    #         # 输出的日志格式
    #         "formatter": "simple",
    #         # 流调用系统输出
    #         "stream": "ext://sys.stdout"
    #     },
    #     # 写入到文件的hanler，写入等级为info，命名为request是为了专门记录一些网络请求日志
    #     "info": {
    #         # 定义写入文件的日志类，此类为按时间分割日志类，还有一些按日志大小分割日志的类等
    #         "class": "logger_handlers.TimedRotatingFileHandlerMP",
    #         # 日志等级
    #         "level": "INFO",
    #         # 日志写入格式，因为要写入到文件后期可能会debug用，所以用了较为详细的standard日志格式
    #         "formatter": "standard",
    #         # 要写入的文件名
    #         "filename": os.path.join(log_root_path, 'default', 'info.log'),
    #         # 分割单位，D日，H小时，M分钟，W星期，一般是以小时或天为单位
    #         # 比如文件名为test.log，到凌晨0点的时候会自动分离出test.log.yyyy-mm-dd
    #         "when": 'D',
    #         'backupCount': 5,  # 备份份数
    #         "encoding": "utf8",
    #         "filters": ["info_filter"]
    #     },
    #     # 写入到文件的hanler，写入等级为warning
    #     "warning": {
    #         # 不再赘述，详细见request logger
    #         "class": "logger_handlers.TimedRotatingFileHandlerMP",
    #         "level": "WARNING",
    #         "formatter": "standard",
    #         "filename": os.path.join(log_root_path, 'default', 'warning.log'),
    #         "when": 'D',
    #         'backupCount': 5,  # 备份份数
    #         "encoding": "utf8",
    #         "filters": ["info_filter"]
    #     },
    #     # 写入到文件的hanler，写入等级为error
    #     "error": {
    #         # 不再赘述，详细见request logger
    #         "class": "logger_handlers.TimedRotatingFileHandlerMP",
    #         "level": "ERROR",
    #         "formatter": "standard",
    #         "filename": os.path.join(log_root_path, 'default', 'error.log'),
    #         "when": 'D',
    #         'backupCount': 5,  # 备份份数
    #         "encoding": "utf8",
    #         "filters": ["info_filter"]
    #     },
    #     # 写入到文件的hanler，写入等级为critical（一般有重大错误的时候才会用到此类打印）
    #     "critical": {
    #         # 不再赘述，详细见request logger
    #         "class": "logger_handlers.TimedRotatingFileHandlerMP",
    #         "level": "CRITICAL",
    #         "formatter": "standard",
    #         "filename": os.path.join(log_root_path, 'default', 'critical.log'),
    #         "when": 'D',
    #         'backupCount': 5,  # 备份份数
    #         "encoding": "utf8",
    #         "filters": ["info_filter"]
    #     },
    # },
    "loggers": {},
    # "loggers": {
    #     # logger名字
    #     "my_logger": {
    #         # logger集成的handler
    #         'handlers': ['debug', 'info', 'warning', 'error', 'critical'],
    #         # logger等级，如果实际执行等级，高于此等级，则不触发此logger，logger中所有的handler均不会被触发
    #         'level': "DEBUG",
    #         # 是否继承root日志，如果继承，root的handler会加入到当前logger的handlers中
    #         'propagate': False
    #     },
    #     # logger名字
    #     "my_request_logger": {
    #         # logger集成的handler
    #         'handlers': ['debug', 'request', 'warning', 'error', 'critical'],
    #         # logger等级，如果实际执行等级，高于此等级，则不触发此logger，logger中所有的handler均不会被触发
    #         'level': "DEBUG",
    #         # 是否继承root日志，如果继承，root的handler会加入到当前logger的handlers中
    #         'propagate': False
    #     },
    # },
    # 基础logger，当不指定logger名称时，默认选择此logger
    # "root": {
    #     'handlers': ['info'],
    #     'level': "DEBUG",
    #     'propagate': False
    # }
}
