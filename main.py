# @Author  : yuanzi
# @Time    : 2024/7/7 9:13
# Copyright (c) <yuanzigsa@gmail.com>

import os
import time
import schedule
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

    agent = Agent()

    # for minute in range(0, 60, 5):
    #     schedule.every().hour.at(f":{minute:02d}").do(agent.collect_sync_task)
    # schedule.every().hour.at(":58").do(agent.push_task)

    schedule.every(1).seconds.do(lambda: agent.collect_sync_task() if int(time.strftime("%S")) % 3 == 0 else None).misfire_grace_time(30)
    schedule.every().minute.at(":34").do(agent.push_task).misfire_grace_time(30)

    while True:
        schedule.run_pending()
        time.sleep(1)
