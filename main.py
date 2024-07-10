# @Author  : yuanzi
# @Time    : 2024/7/7 9:13
# Copyright (c) <yuanzigsa@gmail.com>

import os
import time
from agent.agent import Agent
from agent.monitor import Monitor
from agent.utils import setup_logger
from datetime import datetime


banner = f"""启动PushAgent程序...\n
 ███████                  ██          ██                                ██  
░██░░░░██                ░██         ████     █████                    ░██  
░██   ░██ ██   ██  ██████░██        ██░░██   ██░░░██  █████  ███████  ██████
░███████ ░██  ░██ ██░░░░ ░██████   ██  ░░██ ░██  ░██ ██░░░██░░██░░░██░░░██░ 
░██░░░░  ░██  ░██░░█████ ░██░░░██ ██████████░░██████░███████ ░██  ░██  ░██  
░██      ░██  ░██ ░░░░░██░██  ░██░██░░░░░░██ ░░░░░██░██░░░░  ░██  ░██  ░██  
░██      ░░██████ ██████ ░██  ░██░██     ░██  █████ ░░██████ ███  ░██  ░░██ 
░░        ░░░░░░ ░░░░░░  ░░   ░░ ░░      ░░  ░░░░░   ░░░░░░ ░░░   ░░    ░░  

【程序版本】：v1.0   
【更新时间】：2024/7/7
【系统信息】：{Monitor.get_system_info()}  
【CPU信息】：{Monitor.get_cpu_info()[0]}  {Monitor.get_cpu_info()[1]} cores
【内存总量】：{Monitor.get_total_memory_gb()}GB
【当前路径】：{os.getcwd()}
"""


if __name__ == "__main__":
    logger = setup_logger()
    logger.info(banner)

    # 每隔推送周期内采集次数
    cycle_times = 12
    agent = Agent(cycle_times)

    while True:
        try:
            now = datetime.now()
            second = now.second

            if second % 5 == 0:
                agent.collect_sync_task()

            if second == 56:
                agent.push_task()

        except Exception as e:
            logger.error(f"PushAgent运行发生错误 at {datetime.now()}: {e}")

        time.sleep(1)
