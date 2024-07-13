# @Author  : yuanzi
# @Time    : 2024/7/11 17:06
# Copyright (c) <yuanzigsa@gmail.com>

import time
import requests


def push_to_costumer(global_config, payload, max_retries=3):
    headers = {
        'access_id': global_config['access_id'],
        'need_response': 'true',
        'X-Seq': '1',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    attempt = 0
    while attempt < max_retries:
        try:
            response = requests.request("POST", global_config['push_url'], headers=headers, data=payload)
            if response.status_code == 200:
                print("推送成功")
                print(response.headers)
                return True
            else:
                print(f"推送失败，状态码：{response.status_code}")
        except Exception as e:
            print(f"推送至客户出现异常：{e}")

        attempt += 1
        time.sleep(1)
        print(f"重试推送，第 {attempt} 次")
    print("推送失败，已达到最大重试次数")


url1 = "http://pcdnlog.qq.com:80"
url2 = "http://open.fog.qq.com"
global_config = {
    'access_id': '3b6f53ef-a6d8-11ea-8a8a-6c0b84af356a',
    'push_url': url1,
}

data = "20240710,2024071004,131,d964471a-0d1c-11ef-8537-0242ac110004,3,00:0c:29:80:25:45,121366768,121370591,121374474,121378485,121382624,121387225,121391672,121396179,121402384,121408747,121415140,121421685,1,3	"

push_to_costumer(global_config, data)


