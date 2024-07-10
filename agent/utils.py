# @Author  : yuanzi
# @Time    : 2024/7/7 10:25
# Copyright (c) <yuanzigsa@gmail.com>

import os
import logging
import requests
import datetime
from logging.handlers import TimedRotatingFileHandler
from colorlog import ColoredFormatter


def setup_logger():
    log_directory = 'log'
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    log_file_path = os.path.join(log_directory, 'pushAgent.log')

    # 配置控制台输出的日志格式和颜色
    console_formatter = ColoredFormatter(
        "%(log_color)s%(asctime)s.%(msecs)03d - %(levelname)s - %(message)s",
        datefmt='%Y-%m-%d %H:%M:%S',
        log_colors={
            'ERROR': 'red',
            'WARNING': 'yellow',
            'CRITICAL': 'bold_red',
            'INFO': 'cyan',
            'DEBUG': 'white',
            'NOTSET': 'white'
        }
    )

    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)  # 设置为DEBUG级别以捕获所有级别的日志

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    file_handler = TimedRotatingFileHandler(
        filename=log_file_path, when='midnight', interval=1, backupCount=30, encoding='utf-8'
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.INFO)  # 文件日志默认记录INFO级别及以上的日志
    logger.addHandler(file_handler)

    return logger


# def send_dingtalk_message(info, webhook_url):
#     def send_dingtalk_request(url, data, headers):
#         return requests.post(url, json=data, headers=headers)
#
#     now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#     headers = {'Content-Type': 'application/json'}
#     event_title = f'<font color="#f90202">推送Agent-告警通知</font>'
#     texts = [
#         f'## {event_title}',
#         f'**告警时间：** {now_time}',
#         f'**告警描述：** <font color="#f90202">推送Agent运行出现异常，请管理员检查日志获取详情！~</font>',
#         f'**详细信息：** {info}',
#     ]
#
#     data = {
#         "msgtype": "markdown",
#         "markdown": {
#             "title": "推送Agent运行出现异常",
#             'text': '\n\n'.join(texts)
#         },
#         'at': {
#             'isAtAll': True
#         }
#     }
#     try:
#         for url in eval(webhook_url):
#             response = send_dingtalk_request(url, data, headers)
#             if response.status_code != 200:
#                 logging.warning(" 钉钉消息发送失败，正在重试...")
#                 # 重试发送钉钉消息
#                 retry_count = 3  # 设置重试次数
#                 for i in range(retry_count):
#                     response = send_dingtalk_request(webhook_url, data, headers)
#                     if response.status_code == 200:
#                         break
#             else:
#                 logging.info(f"钉钉告警消息发送请求成功：{response.text}")
#     except Exception as e:
#         logging.error(f"发送钉钉消息出错：{e}")