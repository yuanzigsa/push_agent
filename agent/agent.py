# @Author  : yuanzi
# @Time    : 2024/7/7 10:25
# Copyright (c) <yuanzigsa@gmail.com>

import threading
from agent.monitor import Monitor
from agent.sync import ServerSync
import logging

class Agent:
    def __init__(self, cycle_times):
        self.logger = logging.getLogger()
        self.hardware_collector = Monitor()
        self.server_sync = ServerSync()
        self.cycle_times = cycle_times
        self.collect_data = []

    def collect_sync_task(self):
        info = self.hardware_collector.collect_netifio()
        self.collect_data.append(info)
        if info:
            self.logger.info("流量信息采集成功")
            self.logger.info(f"第【{len(self.collect_data)}/{self.cycle_times}】轮采集完成")
        else:
            self.logger.error(f"第【{len(self.collect_data)}/{self.cycle_times}】轮采集失败")

        info = self.collect_data
        success = self.server_sync.sync(info)
        if success:
            self.logger.info("平台信息同步成功")
        else:
            self.logger.error("平台信息同步失败")

    def push_task(self):
        info = self.collect_data
        success = self.server_sync.push(info, self.cycle_times)
        if success:
            self.logger.info("流量信息推送成功")
        else:
            if success is False:
                self.logger.error("流量信息推送失败,请检查！")

        # 重置采集数据变量，防止大量溢出
        self.collect_data = []
