#!/usr/bin/python3.6+
# -*- coding:utf-8 -*-
"""
@auth: cml
@date: 2020-2-22
@desc: 测试网络拓扑数据的相关函数和类
"""
import unittest
from agent.utils.report_net import (
    report_network,
    fectch_docker_network,
    get_info_by_pid,
    run_process,
    proc_ip_output,
    proc_netstat_output,
)


class TestReportNetTopo(unittest.TestCase):
    # 每执行一个用例，都会执行setup()和teardown()方法
    # 如果跑所有用例，只运行一次前提条件和结束条件。则用setupclass()和teardownclass()
    # def setUp(self):
    #     print("=====测试用例执行前的初始化操作======")
    #
    # def tearDown(self):
    #     print("=====测试用例执行完之后的收尾操作=====")

    # def setUpClass(cls):
    #     pass
    #
    # def tearDownClass(cls):
    #     pass

    def test_proc_netstat_output(self):
        net_str = 'Active Internet connections (w/o servers)\n' \
                  'Proto Recv-Q Send-Q Local Address           Foreign Address         State      \n' \
                  'tcp        0      1 172.18.249.175:37514    108.177.125.82:443      SYN_SENT   \n' \
                  'tcp        0      0 172.18.249.175:50706    100.100.30.25:80        ESTABLISHED\n' \
                  'tcp        0      1 172.18.249.175:43616    64.233.189.82:443       SYN_SENT   \n' \
                  'tcp        0      0 172.18.249.175:22       113.65.10.65:58715      ESTABLISHED\n' \
                  'tcp        0     36 172.18.249.175:22       113.65.10.65:60030      ESTABLISHED\n' \
                  'tcp        0      1 172.18.249.175:37510    108.177.125.82:443      SYN_SENT   \n' \
                  'tcp        0      1 172.18.249.175:37508    108.177.125.82:443      SYN_SENT   '
        res = proc_netstat_output(net_str)
        exp_v = "172.18.249.175:50706+100.100.30.25:80,172.18.249.175:22+113.65.10.65:58715,172.18.249.175:22+113.65.10.65:60030"
        self.assertEqual(res, exp_v, msg='proc_netstat_output 解析有误')

    def test_proc_ip_output(self):
        ip_str = '1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000\n' \
                 '    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00\n' \
                 '    inet 127.0.0.1/8 scope host lo\n' \
                 '       valid_lft forever preferred_lft forever\n' \
                 '2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP group default qlen 1000\n' \
                 '    link/ether 00:16:3e:14:42:b0 brd ff:ff:ff:ff:ff:ff\n' \
                 '    inet 172.18.249.175/20 brd 172.18.255.255 scope global dynamic eth0\n' \
                 '       valid_lft 308351626sec preferred_lft 308351626sec\n' \
                 '3: docker0: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc noqueue state DOWN group default \n' \
                 '    link/ether 02:42:46:7f:9a:46 brd ff:ff:ff:ff:ff:ff\n' \
                 '    inet 172.17.0.1/16 scope global docker0\n' \
                 '       valid_lft forever preferred_lft forever'
        res = proc_ip_output(ip_str)
        exp_v = '172.18.249.175,172.17.0.1'
        self.assertEqual(res, exp_v, msg='proc_ip_output 解析有误')

    def test_run_process(self):
        cmd = "ls"
        data, code = run_process(cmd)
        self.assertEqual(code, 0, msg="subprocess执行命令失败！")

    def test_get_info_by_pid(self):
        res = fectch_docker_network()
        self.assertIsInstance(res, list, msg='输出值应该是个列表')

    def test_get_info_by_pid2(self):
        # TODO: 需要先确认当前测试环境下是否已经运行测试镜像。
        pass


if __name__ == '__main__':
    unittest.main()

