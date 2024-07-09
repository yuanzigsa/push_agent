# @Author  : yuanzi
# @Time    : 2024/7/7 10:25
# Copyright (c) <yuanzigsa@gmail.com>

import threading
import time

import requests

from agent.monitor import Monitor
from agent.sync import ServerSync
import logging


class SharedInfo:
    def __init__(self):
        self.info = []
        self.lock = threading.Lock()
        # self.machine_config = None
        # self.global_config = None


class Agent:
    def __init__(self, collect_sync_interval, push_interval):
        self.logger = logging.getLogger()
        self.shared_info = SharedInfo()
        self.push_interval = push_interval
        self.collect_sync_interval = collect_sync_interval
        self.hardware_collector = Monitor()
        self.server_sync = ServerSync()
        self.total = int(self.push_interval / self.collect_sync_interval)

    def start(self):
        threading.Thread(target=self.collect_sync_task, daemon=True).start()
        threading.Thread(target=self.push_task, daemon=True).start()

        self.logger.info("流量采集线程已启动！")
        self.logger.info("平台同步线程已启动！")
        self.logger.info("流量推送线程已启动！")

    def collect_sync_task(self):
        while True:
            info = self.hardware_collector.collect_netifio()
            with self.shared_info.lock:
                self.shared_info.info.append(info)
                if info:
                    self.logger.info("流量信息采集成功")
                    self.logger.info(f"第【{len(self.shared_info.info)}/{self.total}】轮采集完成")
                else:
                    self.logger.error("第【{len(self.shared_info.info)}/{total}】轮采集失败")

                info = self.shared_info.info
                success = self.server_sync.sync(info)
                if success:
                    self.logger.info("平台信息同步成功")
                else:
                    self.logger.error("平台信息同步失败")
            time.sleep(self.collect_sync_interval)

    def push_task(self):
        while True:
            with self.shared_info.lock:
                info = self.shared_info.info
                success = self.server_sync.push(info, self.total)
                if success:
                    self.logger.info("流量信息推送成功")
                else:
                    if success is False:
                        self.logger.error("流量信息推送失败")

                # 重置采集数据变量，防止大量溢出
                self.shared_info.info = []
            time.sleep(self.push_interval)
