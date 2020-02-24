#!/usr/bin/python3.6+
# -*- coding:utf-8 -*-
"""
@auth: cml
@date: 2020-2-21
@desc: 常量配置文件
"""
import os
from queue import Queue

import docker


# client = docker.DockerClient(base_url='unix://var/run/docker.sock')
# apiRaw = docker.APIClient(base_url='unix://var/run/docker.sock')

E_REPORT_URL = 'http://192.168.3.49:8080/b/event/seceventreport'
CFG_URL = 'http://192.168.3.49:8080/b/config/queryconfig'
NETREPORT_URL = 'http://192.168.3.49:8080/b/status/netstatus.json'
g_nodename = ""
g_podname = ""
g_ruledir = "./falco"

g_queue = Queue()
g_isrun = True


class Settings:
    """
    根据当前环境赋值给变量，供给整个系统调用
    """
    global E_REPORT_URL
    global CFG_URL
    global NETREPORT_URL
    global g_podname
    global g_nodename
    global g_ruledir
    env = os.environ
    report_url = env.get("E_REPORT_URL") or E_REPORT_URL
    config_url = env.get("CFG_URL") or CFG_URL
    net_report_url = env.get("NETREPORT_URL") or NETREPORT_URL
    pod_name = env.get("g_podname") or g_podname
    node_name = env.get("g_nodename") or g_nodename
    rule_dir = env.get("g_ruledir") or g_ruledir

