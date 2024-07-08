# @Author  : yuanzi
# @Time    : 2024/7/7 9:13
# Copyright (c) <yuanzigsa@gmail.com>

import os
import time
from agent.agent import Agent
from agent.monitor import Monitor
from agent.utils import setup_logger

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

【内存总量】：{Monitor.get_total_memory_gb()}GB
【当前路径】：{os.getcwd()}
"""
# 【CPU 信息】：{Monitor.get_cpu_info()[0]}  {Monitor.get_cpu_info()[1]} cores

if __name__ == "__main__":
    logger = setup_logger()
    logger.info(banner)
    # 数据初始化
    sync_interval = 3
    collect_interval = 3
    push_interval = 9

    agent = Agent(sync_interval, collect_interval, push_interval)
    agent.start()

    while True:
        time.sleep(1)
