# @Author  : yuanzi
# @Time    : 2024/7/7 10:26
# Copyright (c) <yuanzigsa@gmail.com>
import json
import time
import logging
import requests
from datetime import datetime


class ServerSync:
    def __init__(self):
        from agent.monitor import Monitor
        self.monitor = Monitor()
        self.logger = logging.getLogger()
        self.config_api = "http://192.168.31.84:8000/agent/config/"
        self.global_config_api = "http://192.168.31.84:8000/agent/global_config/"
        self.history_api = "http://192.168.31.84:8000/agent/history/"
        with open("info/machineTag.info", "r", encoding="utf-8") as f:
            content = f.read()
            content = content.split(":")
        self.machine_id = content[0]
        self.machine_ip = content[1]
        self.headers = {'Content-Type': 'application/json', 'X-Verification-Code': 'c?JQbPWjrz^vyCn{[W(su>@y$nZqS,'}
        try:
            self.machine_config = requests.get(self.config_api, data=self.machine_id, headers=self.headers).json()['data']
            self.global_config = requests.get(self.global_config_api, headers=self.headers).json()['data']
        except Exception as e:
            self.logger.error(f"{e}")

    def sync(self, info, machine_config):
        if machine_config is None:
            machine_config = self.machine_config
            print(machine_config)
        for machine in machine_config:
            # push
            ifname = self.monitor.get_ifname_by_ip(self.machine_ip)

            total_flow = info[-1][ifname]['sent']

            current_time = self.get_time()
            status = "unknown"
            if current_time['timestamp'] - info[-1][ifname]['uptime'] <= 300:
                status = "normal"
            # 初始信息上报
            data = {
                'device_name': machine,
                'total_flow': total_flow,
                'status': status,
                'last_update': current_time['formatted_time'],
                'device_type': 3,
                'isp_id': 1,
                'collect_ifname': ifname
            }
            try:
                response = requests.post(self.config_api, data=json.dumps(data), headers=self.headers)
                if response.status_code == 200:
                    if response.json()['error'] == '':
                        return response.json()['data']
            except requests.RequestException as e:
                return False

            # 同步
            try:
                response = requests.get(self.config_api, data=self.machine_id, headers=self.headers)
                if response.status_code == 200:
                    if response.json()['error'] == '':
                        return response.json()['data']

            except requests.RequestException as e:
                return False

    def push(self,  info, machine_config, global_config):
        # ifname = a
        # for index, ifnames in enumerate(info):
        #     for name in ifnames[index]:
        #         if name == ifname:
        #             ifnames[index][name] = global_config['']

        # 如何根据ip找到对应的网卡名
        # server_url = global_config['server_url']

        # 推送历史
        try:
            response = requests.post(self.history_api, data=json.dumps(info), headers=self.headers)

            if response.status_code == 200:
                if response.json()['error'] == '':
                    return True
        except requests.RequestException as e:
            return False
        # else:
        #     self.logger.info("没有新的流量信息需要同步")

    @staticmethod
    def get_time():
        current_timestamp = int(time.time())
        dt = datetime.fromtimestamp(current_timestamp)
        formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
        flux_day = dt.strftime('%Y%m%d')
        flux_hour = dt.strftime('%Y%m%d%H')
        return {
            'timestamp': current_timestamp,
            'formatted_time': formatted_time,
            'flux_day': flux_day,
            'flux_hour': flux_hour
        }