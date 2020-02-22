#!/usr/bin/python3.6+
# -*- coding:utf-8 -*-
"""
@auth: cml
@date: 2020-2-21
@desc: 检测数据上报manager
"""
import json
import traceback
from datetime import datetime

import requests
import threading

from ..settings import Settings, g_queue
from .logger import get_logger
logger = get_logger(__name__)


class ReportEvent(threading.Thread):
    """消费线程
    从队列里获取falco报告的事件，上报给manager
    """
    def __init__(self, name, agentid):
        self.queue = g_queue
        self.agentid = agentid
        threading.Thread.__init__(self, name=name)

    def run(self):
        while True:
            if not is_running_falco():
                run_falco()
            queue_val = self.queue.get(1, 3)
            logger.info('get data from queue')
            self.proc_data(queue_val)

    def getindex_from_rule(self, rule):
        sp = rule.split('#')
        if len(sp) == 2:
            return sp[0], sp[1]
        else:
            return "0", rule

    def translate_level(self, level):
        """
        安全等级的转换
        """
        level = level.upper()

        if level == 'DEBUG' or level == 'INFO':
            return "INFO"
        elif level == 'NOTICE':
            return 'NOTICE'
        elif level == 'WARNING':
            return "WARNING"
        elif level == 'ERROR' or level == 'CRITICAL':
            return 'ERROR'
        else:
            return 'INFO'

    def translate_time(self, mytime):
        """
        时间格式转换
        """
        mis = 0
        try:
            localtime = None
            if len(mytime) == len('2019-12-19T10:07:11.565737012Z'):
                mytime = mytime[:-4]+"Z"
                UTC_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
                utc_time = datetime.strptime(mytime, UTC_FORMAT)
                localtime = utc_time # + datetime.timedelta(hours=8)

            else:
                localtime = datetime.now()

            mis = int(float(localtime.strftime("%s.%f"))*1000)
        except Exception as e:
            logger.error(e, traceback.format_exc())
            mis = int(float(datetime.now().strftime("%s.%f"))*1000)
        return mis

    def proc_data(self, data):
        """
        获取队列中的falco信息，整理好data传输数据对E_REPORT_URL_发起请求并记录日志
        """
        try:
            # 接收falco json output
            obj = json.loads(data)
            container_id = "N/A"
            if 'container.id' in obj['output_fields']:
                container_id = obj['output_fields']['container.id']

            data = dict()
            data['eventid'], data['eventname'] = self.getindex_from_rule(obj['rule'])
            data['eventdetail'] = obj['output']
            data['level'] = self.translate_level(obj['priority'])
            data['timestamp'] = self.translate_time(obj['time'])

            data['nodename'] = Settings.node_name
            data['containerid'] = container_id
            data['agentid'] = self.agentid
            # data = json.dumps(data)

            logger.info("post to server %s", data)

            r = requests.post(Settings.report_url, json=data)
            logger.info(r.content)

        except Exception as e:
            logger.error('%s %s', e, traceback.format_exc())
