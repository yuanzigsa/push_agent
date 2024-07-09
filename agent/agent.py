# @Author  : yuanzi
# @Time    : 2024/7/7 10:25
# Copyright (c) <yuanzigsa@gmail.com>

import threading
from agent.monitor import Monitor
from agent.sync import ServerSync
import logging


class SharedInfo:
    def __init__(self):
        self.info = []
        self.lock = threading.Lock()


class Agent:
    def __init__(self):
        self.logger = logging.getLogger("AgentLogger")
        self.shared_info = SharedInfo()
        self.hardware_collector = Monitor()
        self.server_sync = ServerSync()
        self.total = 12

    def collect_sync_task(self):
        info = self.hardware_collector.collect_netifio()
        with self.shared_info.lock:
            self.shared_info.info.append(info)
            if info:
                self.logger.info("流量信息采集成功")
                self.logger.info(f"第【{len(self.shared_info.info)}/{self.total}】轮采集完成")
            else:
                self.logger.error(f"第【{len(self.shared_info.info)}/{self.total}】轮采集失败")

            info = self.shared_info.info
            success = self.server_sync.sync(info)
            if success:
                self.logger.info("平台信息同步成功")
            else:
                self.logger.error("平台信息同步失败")

    def push_task(self):
        with self.shared_info.lock:
            info = self.shared_info.info
            success = self.server_sync.push(info, self.total)
            if success:
                self.logger.info("流量信息推送成功")
            else:
                self.logger.error("流量信息推送失败")

            # 重置采集数据变量，防止大量溢出
            self.shared_info.info = []
