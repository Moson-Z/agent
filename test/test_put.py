#!/usr/bin/python3.6+
# -*- coding:utf-8 -*-
"""
@auth: cml
@date: 2020-2-24
@desc: 测试告警规则接口的相关函数和类
"""
import json
import os
import unittest

import docker
import requests
import yaml

from test.test_put_request.settings import Settings
from utils.check import write_versionfile


def tags_type(json_data):
    '''
    检查规则标签,若是字符串转为列表,列表则不变,其他均为空列表
    '''
    for rule in json_data['rule']:
        tags = rule.get('tags')
        if tags and len(tags) > 0:
            if isinstance(tags, str):
                rule['tags'] = tags.split(',')
            elif isinstance(tags, list):
                rule['tags'] = tags
            else:
                rule['tags'] = []
        else:
            rule['tags'] = []
    return json_data

def reload_ubuntu():
    """
    模拟reload_falco
    """
    res = False
    try:
        client = docker.DockerClient(base_url='tcp://0.0.0.0:2376')
        conlist = client.containers.list(all=True)
        falco = None
        for f in conlist:
            if f.name.find('ubuntu_server') != -1:
                falco = f
                break
        if falco is None:
            return res

        client.close()
        res = True
    except Exception as e:
        print("容器操作出错")
    return res

def write_yaml(data):
    YAML_PATH = os.path.join('./test_put_request/falco/', 'falco_rules_1.yaml')
    with open('./test_put_request/falco_rule_null.yaml', 'rb') as fd:
        def_rule = yaml.load(fd)  # 载入只有定义的yaml
    new_rule = def_rule + data['rule']  # 合并yaml数据
    with open(YAML_PATH, 'wb') as fd:
        yaml.safe_dump(new_rule, fd,
                       encoding='utf-8',
                       allow_unicode=True)


class TestPutFalco(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def test_write_versionfile(self):
        ver = b"3.01"
        write_versionfile(ver)
        with open("vers.txt", "rb") as f:
            new_ver = f.read()
        self.assertEqual(ver, new_ver, msg="写入有误")

    def test_tags_type(self):
        json_data = {
                    "rule": [{"rule": "新规则1", "tags": "修改1,修改2,新规则1"},
                            {"rule": "新规则2", "tags": ["修改全部,新规则2"]},
                            {"rule": "新规则3", "tags": {"规则3": "123"}}]
                    }
        rules = tags_type(json_data)["rule"]
        a = 1
        for rule in rules:
            if type(rule["tags"]) != list:
                a = 0
                break
        self.assertEqual(a, 1, msg="格式转换错误")

    def test_reload_falco(self):
        res = reload_ubuntu()
        self.assertEqual(res, True, msg="没有这个容器")

    def test_put(self):
        url = " http://0.0.0.0:8080/proxy"
        data = {
                "code":"1",
                "rule":[{"rule": "新规则1", "tags": "修改1,修改2,新规则1"},
                            {"rule": "新规则2", "tags": ["修改全部,新规则2"]},
                            {"rule": "新规则3", "tags": {"规则3": "123"}}],
                "version":"1"
                }
        ret = requests.put(url, data=json.dumps(data))
        self.assertEqual(ret.json(), {'vid': '1'}, msg="逻辑有误")

    def test_write_yaml(self):
        '''
        放入已经处理好的数据,查看新写入文件是否与原文件一直
        '''
        data = {
                "code":"1",
                "rule":[{"rule": "新规则1", "tags": ["修改1","修改2","新规则1"]},
                            {"rule": "新规则2", "tags": ["修改全部,新规则2"]},
                            {"rule": "新规则3", "tags": []}],
                "version":"1"
                }
        write_yaml(data)
        with open("./test_put_request/falco/falco_rules_1.yaml", "rb") as f:
            data1 = f.read()
        with open("./test_put_request/falco/falco_rules.yaml", "rb") as f:
            data2 = f.read()
        print(data2)

        self.assertEqual(data1, data2, msg="写入yaml失败")

if __name__ == '__main__':
    unittest.main()