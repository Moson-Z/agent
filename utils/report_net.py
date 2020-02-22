#!/usr/bin/python3.6+
# -*- coding:utf-8 -*-
"""
@auth: cml
@date: 2020-2-21
@desc: rule重载
"""
import re

import time
import traceback
import threading
import subprocess

import docker
import requests

from ..settings import Settings
# from .check import fectch_docker_network

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
        while True:  # TODO 处理单例线程运行
            try:
                if count == 0:
                    # self.query_config()
                    report_network()
                elif count == 59:
                    count = -1
                else:
                    time.sleep(1)
                count += 1
            except Exception as e:
                logger.error("%s %s", e, traceback.format_exc())


def report_network():
    """上报网络拓扑数据"""
    repo_list = fectch_docker_network()
    if len(repo_list) > 0:
        try:
            logger.info("report network status...")
            r = requests.post(Settings.net_report_url, json=repo_list)
            logger.info("response %s", r.content)
        except Exception as e:
            logger.error("%s %s", e, traceback.format_exc())

    else:
        logger.info("not find network status")
    return len(repo_list)


def fectch_docker_network():
    """
    获取除pause容器外其他容器的信息
    获取当前node的pod网络拓扑信息，pod由容器组成，所以需要检测host当前所有容器打开端口
    情况和网络连接情况，docker没有提供类似的接口，k8s也没有，所以获取的方法比较底层，用
    nsenter进入指定容器的网络空间再查询：先调用docker接口拿到当前所有container对应的pid，
    再用nsenter进入指定进程的网络空间运行netstat查询连接情况
    （如nsenter --net=/host/proc/15842/ns/net  /host/usr/bin/netstat -tn）
    而对应进程的网络namespace在/proc下面，所以ct-proxy需要特权才能挂载/proc目录。
    由于k8s网络底层架构问题，导致网络拓扑获取非常复杂，故采取这种方式。
    :return:
    """
    # res = True
    repo_list = []

    try:
        api = docker.DockerClient(base_url='unix://var/run/docker.sock')
        api_raw = docker.APIClient(base_url='unix://var/run/docker.sock')
        conlist = api.containers.list()
        for f in conlist:
            try:
                obj = api_raw.inspect_container(f.short_id)
                pid = obj['State']['Pid']
                uid = obj['Id']
                image_name = obj['Config']['Image']
                if image_name.find("pause") != -1:  # 过滤pause容器
                    logger.info("find pause image:%s", image_name)
                    continue

                str_ips, str_nets = get_info_by_pid(pid)
                logger.info("container: %s connect: %s ip:%s", image_name,
                            str_nets, str_ips)

                repo = dict()
                repo['dockerid'] = uid
                repo['nodeid'] = Settings.node_name
                repo['ips'] = str_ips
                repo['connections'] = str_nets
                repo['image'] = image_name
                repo_list.append(repo)
                # post
            except Exception as e:
                logger.error("%s %s", e, traceback.format_exc())

    except Exception as e:
        logger.error("fectchDockerNetwork %s %s", e, traceback.format_exc())

    return repo_list


def get_info_by_pid(pid):
    # /host/proc/
    # /host/usr/bin/
    # /host/usr/bin/nsenter --net=/host/proc/15842/ns/net  /host/usr/bin/netstat -tn
    # /host/usr/bin/nsenter --net=/host/proc/15842/ns/net  ip addr
    proc_path = "/proc"
    usr_path = "/usr/bin"
    netstat_cmd = f"{usr_path}/nsenter --net={proc_path}/{pid}/ns/net {usr_path}/netstat -tn"
    ip_cmd = f"{usr_path}/nsenter --net={proc_path}/{pid}/ns/net ip addr"

    str_net, res_code = run_process(netstat_cmd)
    str_ip, res_code = run_process(ip_cmd)

    str_net_obj = proc_netstat_output(str_net)
    str_ip_obj = proc_ip_output(str_ip)  # 记录下所有不为127.0.0.1的ip

    return str_ip_obj, str_net_obj


def run_process(str_cmd):
    """
    执行命令，获取命令执行结果和结果状态
    """
    try:
        # s = subprocess.Popen(strCmd, shell=False,
        #                      stdout=subprocess.PIPE,
        #                      stderr=subprocess.PIPE)
        exitcode, data = subprocess.getstatusoutput(str_cmd)
    except Exception as e:
        logger.error("cmd error %s %s", str_cmd, e)
        data = ""
        exitcode = -1
    return data, exitcode


def proc_ip_output(ipaddr_str):
    """
    [inet 127.0.0.1,inet 127.0.0.x]
    记录下所有不为127.0.0.1的ip
    """
    ip_str = ""
    try:
        result = re.findall(
            r"\binet (?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}"
            r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b",
            ipaddr_str)
        for r in result:
            ip = r.replace("inet ", "")
            if ip != "127.0.0.1":
                if len(ip_str) > 0:
                    ip_str += ","
                ip_str += ip
    except Exception as e:
        logger.error("error %s %s", e, traceback.format_exc())
    return ip_str


def proc_netstat_output(net_str):
    """
    根据传入的响应信息，正则匹配获取需要信息返回
    """
    str_connects = ""

    try:
        line = net_str.split("\n")
        for l in line:
            if l.find("ESTABLISHED") == -1:
                continue
            result = re.findall(
                r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}"
                r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\:\d+\b",
                l)
            if len(result) != 2:
                continue
            connect = "%s+%s" % (result[0], result[1])
            if len(str_connects) != 0:
                str_connects += ","

            str_connects += connect
    except Exception as e:
        logger.error("error %s %s", e, traceback.format_exc())
    return str_connects





