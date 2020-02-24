import os

import yaml

from flask import request
from flask_restful import Resource

from utils.process_falco import reload_falco
from settings import Settings
from utils.check import write_versionfile

# 需要写入的规则文件的路径
YAML_PATH = os.path.join(Settings.rule_dir, 'falco_rules.yaml')

class ApiViews(Resource):
    def put(self):
        """
        （1）manager下发修改的rule数据
        （3）如果判断是新版本，将标签转换为字典后读取falco_rule_null.yaml内容，
        加上新规则一起写入falco_rules.yaml，并日志记录
        （4）通知falco重启，记录新的版本号，并写入var.txt
        """
        json_data = request.get_json(force=True)
        if json_data["code"] == "1":  # 有新版本数据
            print(json_data)
            # logger.info("query new rule version %s", json_data['version'])
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
            with open('falco_rule_null.yaml', 'rb') as fd:
                def_rule = yaml.load(fd)             # 载入只有定义的yaml
            new_rule = def_rule + json_data['rule']  # 合并yaml数据
            # logger.info("write to %s", YAML_PATH)    # 写入新的yaml
            with open(YAML_PATH, 'wb') as fd:
                yaml.safe_dump(new_rule, fd,
                               encoding='utf-8',
                               allow_unicode=True)
            # 通知falco重启
            # if reload_falco() is False:
            #     print("reloadFaloc")
            #     return
            # 记录新的版本记录
            write_versionfile(json_data['version'])
        # TODO:数据的返回格式不符合RESTful风格，需要改
        return {'vid': "1"}