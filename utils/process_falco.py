#!/usr/bin/python3.6+
# -*- coding:utf-8 -*-
"""
@auth: cml
@date: 2020-2-21
@desc: ...
"""
import docker
import traceback
from .logger import get_logger
logger = get_logger(__name__)


def run_falco():
    pass

def is_running_falco():
    pass


def find_falcoid(client):
    """
    查找falco id（还未被使用）
    """
    falco = client.containers.list()


def reload_falco():
    """
    重启falco
    """
    res = False
    try:
        logger.info("reloadFalco ...")
        client = docker.DockerClient(base_url='unix://var/run/docker.sock')
        logger.info("get Falco container ...")
        conlist = client.containers.list()
        falco = None
        for f in conlist:
            if f.name.find('falco') != -1:
                falco = f
                logger.info('find falco %s', f.name)
                break
        if falco is None:
            logger.error("can't find falco")
            return res

        logger.info("sigal SIGHUP to falco ...")
        falco.kill("SIGHUP")
        logger.info("sigal SIGHUP to falco [OK]")
        client.close()
        res = True
    except Exception as e:
        logger.error("%s %s ", e, traceback.format_exc())
    return res