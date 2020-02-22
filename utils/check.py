#!/usr/bin/python3.6+
# -*- coding:utf-8 -*-
"""
@auth: cml
@date: 2020-2-21
@desc: 系统检测信息
"""
import re
import subprocess
import traceback

import docker

from settings import Settings
from utils.logger import get_logger
logger = get_logger(__name__)


def load_versionfile():
    """
    获取版本信息
    """
    ver = "0"
    try:
        with open("vers.txt", "rb") as fd:
            ver = fd.read()
    except Exception as e:
        logger.error("%s %s", re, traceback)
    return ver


def write_versionfile(ver):
    """
    写入版本信息
    """
    try:
        with open("vers.txt", "wb") as fd:
            fd.write(ver)
    except Exception as e:
        logger.error("%s %s", e, traceback)


def query_docker_id():
    """获取agent容器的id"""
    pod_name = Settings.pod_name
    if Settings.pod_name:
        logger.info("get container id %s use podname", pod_name)
        return pod_name

    dockerid = "N/A"
    try:
        logger.info("get container id ...")
        with open('/proc/1/cpuset', 'rb') as fd:
            dockerid = fd.read()

        if len(dockerid) > 9:
            dockerid = dockerid[8:]

    except Exception as e:
        logger.error(e, traceback.format_exc())

    logger.info("get container id %s", dockerid)
    return dockerid


def run_get_infobypid(pid):
    # /host/proc/
    # /host/usr/bin/
    # /host/usr/bin/nsenter --net=/host/proc/15842/ns/net  /host/usr/bin/netstat -tn
    # /host/usr/bin/nsenter --net=/host/proc/15842/ns/net  ip addr
    PROC_PATH = "/host/proc"
    USR_PATH = "/host/usr/bin"
    netstat_cmd = "%s/nsenter --net=%s/%s/ns/net %s/netstat -tn" % (USR_PATH, PROC_PATH, pid, USR_PATH )
    ip_cmd = "%s/nsenter --net=%s/%s/ns/net ip addr" % (USR_PATH, PROC_PATH, pid)
    print(netstat_cmd)
    print(ip_cmd)
    str_net, res_code = run_process(netstat_cmd.split(" "))
    str_ip, res_code = run_process(ip_cmd.split(" "))

    str_net_obj = ""
    str_ip_obj = ""

    str_net_obj = proc_netstat_output(str_net, logger)
    str_ip_obj = proc_ip_output(str_ip, logger)  #记录下所有不为127.0.0.1的ip

    return str_ip_obj, str_net_obj


def proc_ip_output(strNet):
    """
    [inet 127.0.0.1,inet 127.0.0.x]
    记录下所有不为127.0.0.1的ip
    """
    strIp = ""
    try:
        result = re.findall(r"\binet (?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b",strNet)
        for r in result:
            ip = r.replace("inet ","")
            if ip != "127.0.0.1":
                if len(strIp)>0:
                    strIp+= ","
                strIp+=ip
    except Exception as e:
        logger.error("error %s %s",e,traceback.format_exc())
    return strIp


def run_process(strCmd):
    """
    创建子进程,获取请求响应信息和结束进程状态
    """
    str_res = ""
    res_code = -1
    try:
        # logger.info("### run '%s'",str)
        s = subprocess.Popen(strCmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        while True:
            line = s.stdout.readline()
            if line != b'':
                str_res += line   # line.rstrip()
                # print line.rstrip()
            else:
                break
        s.wait()
        res_code = s.returncode
        # strRes = strRes.decode("GBK")
    except Exception as e:
        logger.error("cmd error %s %s", strCmd, e)

    return str_res, res_code


def proc_netstat_output(strNet):
    """
    根据传入的响应信息，正则匹配获取需要信息返回
    """
    str_connects = ""

    try:
        line = strNet.split("\n")
        for l in line:
            if l.find("ESTABLISHED") == -1:
                continue
            result = re.findall(r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\:\d+\b",l)
            if len(result) != 2:
                continue
            connect = "%s+%s"%(result[0], result[1])
            if len(str_connects) != 0:
                str_connects += ","

            str_connects += connect
    except Exception as e:
        logger.error("error %s %s", e, traceback.format_exc())
    return str_connects


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
    logger.info("fectchDockerNetwork ...")
    # res = True
    repoList = []

    # global g_nodename
    try:
        api = docker.DockerClient(base_url='unix://var/run/docker.sock')
        apiRaw = docker.APIClient(base_url='unix://var/run/docker.sock')
        conlist = api.containers.list()
        for f in conlist:
            try:
                obj = apiRaw.inspect_container(f.short_id)
                pid = obj['State']['Pid']
                uId = obj['Id']
                imageName = obj['Config']['Image']
                if imageName.find("pause") != -1:  # 过滤pause容器
                    logger.info("find pause image:%s", imageName)
                    continue

                strIpObj,strNetObj = run_get_infobypid(pid)
                logger.info("container: %s connect: %s ip:%s", imageName, strNetObj, strIpObj)

                repo = {}
                repo['dockerid'] = uId
                repo['nodeid'] = Settings.node_name
                repo['ips'] = strIpObj
                repo['connections'] = strNetObj
                repo['image'] = imageName
                repoList.append(repo)
                #post
            except Exception as e:
                logger.error("%s %s",e,traceback.format_exc())

    except Exception as e:
        logger.error("fectchDockerNetwork %s %s",e,traceback.format_exc())

    return repoList


if __name__ == '__main__':
    run_get_infobypid()
