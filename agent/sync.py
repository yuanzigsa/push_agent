# @Author  : yuanzi
# @Time    : 2024/7/7 10:26
# Copyright (c) <yuanzigsa@gmail.com>

import re
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
        # self.config_api = "http://192.168.31.84:8000/agent/config/"
        # self.global_config_api = "http://192.168.31.84:8000/agent/get_global_config/"
        # self.history_api = "http://192.168.31.84:8000/agent/history/"
        self.config_api = "http://120.26.111.213:8999/agent/config/"
        self.global_config_api = "http://120.26.111.213:8999/agent/get_global_config/"
        self.history_api = "http://120.26.111.213:8999/agent/history/"
        with open("info/machineTag.info", "r", encoding="utf-8") as f:
            content = f.read().strip().split(":")
        self.machine_id = content[0]
        self.machine_ip = content[1]
        # with open("info/access_token", "r", encoding="utf-8") as f:
        #     content = f.read()
        #     content.replace("\n", "")
        #     content.replace(" ", "")
        self.headers = {'Content-Type': 'application/json', 'X-Verification-Code': "c?JQbPWjrz^vyCn{[W(su>@y$"}
        self.machine_config = None
        self.global_config = None
        self.logger.info("从控制平台获取配置...")
        success = self.get_config()
        if success:
            self.logger.info("从控制平台获取配置成功！")
        else:
            self.logger.error("从控制平台获取配置失败！")

    def get_config(self):
        try:
            machine_config_response = requests.get(self.config_api, data=self.machine_id, headers=self.headers)
            global_config_response = requests.get(self.global_config_api, headers=self.headers)
            machine_config = machine_config_response.json().get('data')
            global_config = global_config_response.json().get('data')

            if global_config is not None:
                self.global_config = global_config

            if machine_config is not None:
                self.machine_config = machine_config
                return True
            else:
                return False
        except Exception as e:
            self.logger.error(f"请求出现异常：{e}")
            return False

    def sync(self, info):
        # 从平台获取配置
        success = self.get_config()

        if success:
            self.logger.info("从控制平台同步成功！")
            self.logger.info(f"【本机配置】：{self.machine_config}")
            self.logger.info(f"【全局配置】：{self.global_config}")
        else:
            self.logger.error("从控制平台同步失败！")

        machine_config = self.machine_config

        self.logger.info(f"【采集数据】:{info}")
        if machine_config is None:
            return False

        # 获取设备名称
        self.logger.info(f"【机器IP】:{self.machine_ip}")

        ifname = self.monitor.get_ifname_by_ip(self.machine_ip)
        self.logger.info(f"【根据IP获得的网卡名】:{ifname}")



        device_name = next(iter(machine_config))
        # 获取采集接口
        ifconfig = machine_config[device_name]
        if ifconfig is not None:

            ifname = ifconfig['collect_ifname']
        self.logger.info(f"【当前采集接口】:{ifname}")


        total_flow = info[-1][ifname]['sent']
        current_time = self.get_time()
        status = "unknown"
        if current_time['timestamp'] - info[-1][ifname]['uptime'] <= 300:
            status = "normal"

        # 初始信息上报
        data = {
            'device_name': device_name,
            'total_flow': total_flow,
            'status': status,
            'last_update': current_time['formatted_time'],
            # 'device_type': 3,
            # 'isp_id': 1,
            'collect_ifname': ifname,
            'interfaces': ",".join([str(ifname) for ifname in info[-1].keys()]),
            'mac': info[-1][ifname]['mac'],
        }
        try:
            response = requests.post(self.config_api, data=json.dumps(data), headers=self.headers)
            self.logger.info(f"【{device_name}】上报平台信息：{data}")
            if response.status_code == 200:
                if response.json()['error'] == '':
                    return True
                else:
                    return False
            else:
                return False
        except requests.RequestException as e:
            self.logger.error(f"请求出现异常：{e}")
            return False

    def push(self, info, cycle_times):
        if len(info) != cycle_times:
            return

        # 推送至客户
        machine_config = self.machine_config
        global_config = self.global_config

        if global_config is None:
            self.logger.error("全局配置为空，无法推送数据")
            return

        device_name = next(iter(machine_config))
        if machine_config[device_name]["disabled"] == "yes":
            self.logger.warning(f"【{device_name}】已关闭流量推送")
            return

        current_time = self.get_time()

        data = [
            current_time['flux_day'],
            current_time['flux_hour'],
            global_config['provider_id'],
            global_config['provider_uiid'],
            machine_config[device_name]['isp_id'],
            machine_config[device_name]['mac'],
        ]
        # 数据是否需要进行偏移量调整
        values = []
        for ifinfo in info:
            value = ifinfo[machine_config[device_name]['collect_ifname']]['sent']
            value_modify = machine_config[device_name]['value_modify']
            value_modify = str(value_modify)
            numbers = re.findall(r'\d+\.?\d*', value_modify)
            if "+" in value_modify:
                value = int(value) + int(numbers[0])
            elif "-" in value_modify:
                value = int(value) - int(numbers[0])
            values.append(value)

        # 加上本周期采集数据
        data.extend(values)

        version = 1
        data.append(version)
        data.append(machine_config[device_name]['device_type'])

        playload = ','.join([str(item) for item in data])

        self.logger.info(f"【{device_name}】推送数据：{playload}")

        headers = {
            'access_id': global_config['access_id'],
            'need_response': 'true',
            'X-Seq': '1',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        success = self.push_to_costumer(global_config, playload, headers)
        if success:
            # 更新历史记录
            self.update_history(device_name, "success", ','.join([str(item) for item in values]), current_time['formatted_time'])
            return True
        else:
            # 更新历史记录，钉钉告警
            self.update_history(device_name, "faild", ','.join([str(item) for item in values]), current_time['formatted_time'])
            return False

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

    def push_to_costumer(self, global_config, payload, headers, max_retries=3):
        attempt = 0
        while attempt < max_retries:
            try:
                response = requests.request("POST", global_config['push_url'], data=payload, headers=headers)
                if response.status_code == 200:
                    return True
                else:
                    self.logger.error(f"推送失败，状态码：{response.status_code}")
            except Exception as e:
                self.logger.error(f"推送至客户出现异常：{e}")

            attempt += 1
            time.sleep(1)
            self.logger.warning(f"重试推送，第 {attempt} 次")
        self.logger.error("推送失败，已达到最大重试次数")

    def update_history(self, device_name, status, push_info, uptime, max_retries=3):
        self.logger.info(f"开始更新历史记录......")
        info = {
            "device_name": device_name,
            "status": status,
            "push_info": push_info,
            "uptime": uptime
        }
        attempt = 0
        while attempt < max_retries:
            try:
                response = requests.post(self.history_api, data=json.dumps(info), headers=self.headers)
                if response.status_code == 200:
                    self.logger.info("更新历史记录成功")
                    return True
                else:
                    self.logger.error(f"更新历史记录失败，状态码：{response.status_code}")
            except Exception as e:
                self.logger.error(f"更新历史记录出现异常：{e}")
            attempt += 1
            time.sleep(1)
            self.logger.warning(f"重试推送，第 {attempt} 次")
        self.logger.error("更新失败，已达到最大重试次数")
        return False
