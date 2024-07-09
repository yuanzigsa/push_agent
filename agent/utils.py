# @Author  : yuanzi
# @Time    : 2024/7/7 10:25
# Copyright (c) <yuanzigsa@gmail.com>

import os
import logging
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
    logger.setLevel(logging.DEBUG)  # 设置为DEBUG级别以捕获所有级别的日志

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


def send_dingtalk_message(message, url):
    pass