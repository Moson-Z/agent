#!/usr/bin/env python3.5+
# -*- coding: utf-8 -*-
"""
@auth: cml
@date: 2020-2-21
@desc: 根据应用来分类日志，每个应用下都有六种日志模式：
        ['debug', 'request', 'warning', 'error', 'critical', 'request']
"""
import os
import sys
sys.path.append(os.path.dirname(os.pardir))

import re
SYS_ENV = 'win' if re.search('[Ww]in', sys.platform) else 'unix'

import logging
import logging.config
from .logger_config import log_root_path, LOGGING
# from settings import SYS_ENV
# from logging.config import dictConfig
# from logging.handlers import TimedRotatingFileHandler


class Logger:

    # 单例模式存储对象
    __instance = {}
    __is_init = False

    # 对于每个app name单例模式
    def __new__(cls, app_name='default', *args, **kwargs):
        if app_name not in cls.__instance:
            cls.__instance[app_name] = super().__new__(cls)
        return cls.__instance[app_name]

    # 初始化logger，通过LOGGING配置logger
    def __init__(self, app_name='default', is_debug=True):
        if self.__is_init is True:
            return
        log_file_dir = os.path.join(log_root_path, app_name)
        print("app名为%s的日志被初始化了，日志会写入到：%s 文件夹下" % (app_name, log_file_dir))
        self.__is_init = True
        self.is_debug = is_debug

        # 初始化logging配置参数
        # global LOGGING
        # 默认路径为logs目录下的default目录 ./logs/default
        self.default_log_path = os.path.join(log_root_path, 'default')
        # # 默认路径为当前文件所在目录的兄弟目录logs下的app_name目录 ./logs/${app_name}
        self.log_cur_path = os.path.join(log_root_path, app_name)

        if not os.path.exists(self.log_cur_path):      # 不存在就创建default目录
            os.makedirs(self.log_cur_path)
        if not os.path.exists(self.default_log_path):  # 不存在就创建当前app_name对应的目录
            os.makedirs(self.default_log_path)

        # 日志名和日志等级的映射
        log_levels = ['debug', 'info', 'warning', 'error',  'critical']

        # 根据app_name动态更新LOGGING配置，为每个app_name创建文件夹，配置handler
        for level in log_levels:
            # handler名称，如default_debug
            handler_name = '%s_%s' % (app_name, level)
            if level == 'debug':
                LOGGING['handlers'][handler_name] = self.get_console_handler_conf()
                # 日志名称，如default_debug_logger
            else:
                # handler 对应文件名，如 logs/default/request.log
                filename = os.path.join(self.log_cur_path, (level + '.log'))
                # 日志等级转大写
                lev_up = level.upper()
                LOGGING['handlers'][handler_name] = self.get_file_handler_conf(
                    filename=filename, level=lev_up)
                # 日志名称，如default_error_logger
        # 单独初始化request handler
        request_filename = os.path.join(self.log_cur_path, 'request.log')
        request_handler_name = '%s_request' % app_name
        # 绑定request handler
        LOGGING['handlers'][request_handler_name] = self.get_file_handler_conf(
            filename=request_filename, level="INFO")

        # 添加app logger及app_request logger
        logger_name = '%s_logger' % app_name
        LOGGING['loggers'][logger_name] = self.get_log_conf(app_name=app_name)
        request_logname = '%s_request_logger' % app_name
        LOGGING['loggers'][request_logname] = self.get_req_log_conf(app_name=app_name)

        logging.config.dictConfig(LOGGING)  # 将LOGGING中的配置信息更新到logging中

        # 这里之所以要分6种logger，而不是只写一种logger，是为了将不同等级的日志信息，
        # 写入到不同的文件中，方便后期的debug和统计
        self.debug_logger = logging.getLogger("%s_debug_logger" % app_name)       # 获取debug日志，用于只打印到控制台，不写入文件的日志，一般用于打印较长的sql，或是一大段json字符串
        self.request_logger = logging.getLogger("%s_request_logger" % app_name)   # 获取request日志，一般用于记录请求日志，可以在用户开始访问和访问成功的时间点分别记录日志，可以统计访问的成功率
        self.info_logger = logging.getLogger("%s_info_logger" % app_name)         # 获取info日志，也是最长用的一种日志，用于记录日常业务中的各种行为，是最灵活，使用最广泛的一种日志
        self.warning_logger = logging.getLogger("%s_warning_logger" % app_name)   # 获取warning日志，一般用于有一些小错误或瑕疵，但不影响程序运行的行为的警告
        self.error_logger = logging.getLogger("%s_error_logger" % app_name)       # 获取error日志，一般用于主动的错误提示，或者被动的捕获异常时的异常记录日志，常和try。。。except一起使用
        self.critical_logger = logging.getLogger("%s_critical_logger" % app_name) # 获取critical日志，用于重大异常，可能影响整体项目运行的异常

    # 控制台输出handler配置
    def get_console_handler_conf(self):
        console_handler_conf = {
            # 定义输出流的类
            "class": "logging.StreamHandler",
            # handler等级，如果实际执行等级高于此等级，则不触发handler
            "level": "DEBUG",
            # 输出的日志格式
            "formatter": "simple",
            # 流调用系统输出
            "stream": "ext://sys.stdout"
        }
        if self.is_debug:
            console_handler_conf['filters'] = ['debug_filter']
        else:
            console_handler_conf['filters'] = ['no_debug_filter']
        return console_handler_conf

    @staticmethod
    # 写入文件handler配置
    def get_file_handler_conf(filename: str, level='INFO'):
        file_handler_conf = {
            "class": "logger_handlers.TimedRotatingFileHandlerMP",  # 定义写入文件的日志类，此类为按时间分割日志类，还有一些按日志大小分割日志的类等
            "level": "",  # 日志等级
            "formatter": "standard",  # 日志写入格式，因为要写入到文件后期可能会debug用，所以用了较为详细的standard日志格式
            "filename": '',  # 要写入的文件名
            "when": 'D',  # 分割单位，D日，H小时，M分钟，W星期，一般是以小时或天为单位,比如文件名为test.log，到凌晨0点的时候会自动分离出test.log.yyyy-mm-dd
            "backupCount": 5,  # 备份份数
            "encoding": "utf8",
            "filters": []
        }
        if SYS_ENV == 'win':
            file_handler_conf['class'] = 'logging.handlers.TimedRotatingFileHandler'
        filters = ['%s_filter' % (level.lower())]
        update_dict = {'filename': filename, 'level': level, 'filters': filters}
        file_handler_conf.update(update_dict)
        return file_handler_conf

    @staticmethod
    def get_log_conf(app_name='default'):
        """获取logger 配置"""
        logger_conf = {
            'handlers': [],
            'level': "DEBUG",
            'propagate': False
        }
        # 如果只是debug级别logger，只配置打印handler，不会记录到文件中
        log_levels = ['debug', 'info', 'warning', 'error', 'critical']
        logger_conf['handlers'] = ['%s_%s' % (app_name, level) for level in log_levels]
        return logger_conf

    @staticmethod
    def get_req_log_conf(app_name='default'):
        """获取request logger配置"""
        logger_conf = {
            'handlers': [],
            'level': "DEBUG",
            'propagate': False
        }
        log_levels = ['debug', 'request', 'warning', 'error', 'critical']
        logger_conf['handlers'] = ['%s_%s' % (app_name, level) for level in log_levels]
        return logger_conf


# 获取日常logger
def get_logger(app_name: str, is_debug=True):
    Logger(app_name, is_debug=is_debug)
    logger_name = '%s_logger' % app_name
    logger = logging.getLogger(logger_name)
    return logger


# 获取request logger
def get_request_logger(app_name: str, is_debug=True):
    Logger(app_name, is_debug=is_debug)
    logger_name = '%s_request_logger' % app_name
    logger = logging.getLogger(logger_name)
    return logger


if __name__ == '__main__':
    # 单例模式测试
    logger = get_request_logger('cml_test', is_debug=True)

    logger.error('error log')
    logger.debug('debug log')
    logger.debug('debug log')