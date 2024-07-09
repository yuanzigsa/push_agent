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

    # for minute in range(0, 60, 5):
    #     schedule.every().hour.at(f":{minute:02d}").do(agent.collect_sync_task)
    # schedule.every().hour.at(":58").do(agent.push_task)

    schedule.every().minute.at(":00").do(lambda: agent.collect_sync_task if int(time.strftime("%S")) % 5 == 0 else None)
    schedule.every().minute.at(":59").do(agent.push_task)

    while True:
        schedule.run_pending()
        time.sleep(1)
