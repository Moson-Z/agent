#!/usr/bin/python3.6+
# -*- coding:utf-8 -*-
"""
@auth: cml
@date: 2020-2-21
@desc: rule重载
"""
import datetime
import json
import os
import re
import threading

import time
import traceback

import docker
import requests
import yaml

from ..settings import Settings
from .check import fectch_docker_network

from .logger import get_logger
logger = get_logger(__name__)


class ReportNetTopo(threading.Thread):
    """定时上报网络拓扑数据"""
    def __init__(self, t_name, agent_id):
        self.agent_id = agent_id
        threading.Thread.__init__(self, name=t_name)

    def run(self):
        """
        定时执行任务：
        第一次运行，更新规则，然后上报manager
        30秒监测一次版本更新，若有更新，重新也如yaml文件
        60秒查看一次容器数量，上报manager
        :return:
        """
        count = 0
        while g_isrun:  # TODO 处理单例线程运行
            try:
                if count == 0:
                    # self.query_config()
                    self.report_network()
                elif count == 59:
                    count = -1
                else:
                    time.sleep(1)
                count += 1
            except Exception as e:
                logger.error("%s %s", e, traceback.format_exc())

    @staticmethod
    def report_network():
        repoList = fectch_docker_network()
        if len(repoList) > 0:
            try:
                logger.info("report network status...")
                r = requests.post(Settings.net_report_url, json=repoList)
                logger.info("response %s", r.content)
            except Exception as e:
                logger.error("%s %s", e, traceback.format_exc())

        else:
            logger.info("not find network status")
        return len(repoList)



