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
        self.machine_config = None
        self.global_config = None


class Agent:
    def __init__(self, sync_interval, collect_interval, push_interval):
        self.logger = logging.getLogger()
        self.shared_info = SharedInfo()
        self.push_interval = push_interval
        self.collect_interval = collect_interval
        self.sync_interval = sync_interval
        self.hardware_collector = Monitor()
        self.server_sync = ServerSync()
        # 事件对象用于同步线程启动顺序
        self.collect_event = threading.Event()
        self.sync_event = threading.Event()
        self.push_event = threading.Event()
        self.total = int(self.push_interval / self.collect_interval)

    def start(self):
        threading.Thread(target=self.collect_task, daemon=True).start()
        self.collect_event.wait()  # 等待 collect_task 完成第一次任务
        self.logger.info("流量采集线程已启动！")
        threading.Thread(target=self.sync_task, daemon=True).start()
        self.logger.info("平台同步线程已启动！")
        self.sync_event.wait()  # 等待 sync_task 完成第一次任务
        threading.Thread(target=self.push_task, daemon=True).start()
        self.logger.info("流量推送线程已启动！")

    def collect_task(self):
        while True:

            info = self.hardware_collector.collect_netifio()

            with self.shared_info.lock:
                self.shared_info.info.append(info)

            if info:
                self.logger.info("流量信息采集成功")
                self.logger.info(f"第【{len(self.shared_info.info)}/{self.total}】轮采集完成")
            else:
                self.logger.error("第【{len(self.shared_info.info)}/{total}】轮采集失败")

            if not self.collect_event.is_set():
                self.collect_event.set()  # 第一次任务完成后设置事件
            time.sleep(self.collect_interval)

    def sync_task(self):
        while True:
            # 推送信息、从服务器获取配置并进行比对
            with self.shared_info.lock:
                info = self.shared_info.info
                success = self.server_sync.sync(info, self.shared_info.machine_config)
                if success:
                    self.logger.info("平台信息同步成功")
                    if self.shared_info.machine_config != success:
                        self.shared_info.machine_config = success
                else:
                    self.logger.error("平台信息同步失败")
            if not self.sync_event.is_set():
                self.sync_event.set()  # 第一次任务完成后设置事件
            time.sleep(self.sync_interval)

    def push_task(self):
        while True:
            with self.shared_info.lock:
                info = self.shared_info.info
                success = self.server_sync.push(info, self.shared_info.machine_config, self.shared_info.global_config, self.total)
                if success:
                    self.logger.info("流量信息推送成功")
                    # 重置采集数据变量
                    self.shared_info.info = []
                else:
                    if success is False:
                        self.logger.error("流量信息推送失败")
            if not self.push_event.is_set():
                self.push_event.set()  # 第一次任务完成后设置事件
            time.sleep(self.push_interval)
