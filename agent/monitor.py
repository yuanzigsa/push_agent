# @Author  : yuanzi
# @Time    : 2024/7/7 10:26
# Copyright (c) <yuanzigsa@gmail.com>

import socket
import psutil
import platform
from agent.sync import ServerSync


class Monitor:
    def __init__(self):
        pass

    def collect_netifio(self):
        # 获取所有网络接口
        # 定义物理网卡的前缀
        physical_interfaces_prefixes = ('eth', 'em', 'en', 'wlan', 'wifi')

        # 获取所有网络接口
        if_addrs = psutil.net_if_addrs()
        if_io = psutil.net_io_counters(pernic=True)

        interfaces = {}

        for ifname in if_addrs:
            # 检查接口名称是否以物理网卡前缀开头
            # if any(ifname.startswith(prefix) for prefix in physical_interfaces_prefixes):
                # 获取 MAC 地址和 IP 地址
                mac_address = ''
                ip_address = ''
                for addr in if_addrs[ifname]:
                    if addr.family == psutil.AF_LINK:
                        mac_address = addr.address
                    elif addr.family == socket.AF_INET:
                        ip_address = addr.address

                # 获取发送和接收字节数
                sent_bytes = if_io[ifname].bytes_sent if ifname in if_io else 0
                recv_bytes = if_io[ifname].bytes_recv if ifname in if_io else 0

                # 添加到结果字典
                interfaces[ifname] = {
                    'uptime': ServerSync.get_time()['timestamp'],
                    'mac': mac_address,
                    'ip': ip_address,
                    'sent': sent_bytes,
                    'recv': recv_bytes
                }
        return interfaces

    @staticmethod
    def get_system_info():
        system_info = platform.platform()
        return system_info

    @staticmethod
    def get_cpu_info():
        try:
            with open('/proc/cpuinfo', 'r') as file:
                for line in file:
                    if line.strip().startswith("model name"):
                        cpu_model = line.split(":")[1].strip()
                        # cpu_info = f"Model: {cpu_model}"
                        break
        except FileNotFoundError:
            pass

    @staticmethod
    def get_total_memory_gb():
        memory_info = psutil.virtual_memory()
        total_memory_bytes = memory_info.total
        total_memory_gb = round(total_memory_bytes / (1024 ** 3))
        return total_memory_gb

    @staticmethod
    def get_ifname_by_ip(ip_address):
        for interface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == socket.AF_INET and addr.address == ip_address:
                    return interface
        return None

