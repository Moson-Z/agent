#!/usr/bin/python3.6+
# -*- coding:utf-8 -*-
"""
@auth: cml
@date: 2020-2-21
@desc: Flask服务器启动
"""
from flask import Flask
from flask_restful import Api

from test.test_put_request.view import ApiViews
# from .utils.check import query_docker_id
# from .utils.report_net import ReportNetTopo
# from .utils.report_event import ReportEvent

app = Flask(__name__, static_url_path='/')
api = Api(app)

api.add_resource(ApiViews, '/proxy')


if __name__ == '__main__':
    # init()  # yaml文件复制，考虑在镜像制作的时候完成
    # agent_id = query_docker_id()
    # cl = ReportNetTopo('ReportNetTopo', agent_id)
    # cl.start()
    # consume = ReportEvent('ReportEvent', agent_id)
    # consume.start()

    app.run(host='0.0.0.0', port=8080, debug=True)