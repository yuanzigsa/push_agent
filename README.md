# 一、项目背景
出于客户流量上报的要求，作为服务供应商需要开发一个流量上报程序，实时采集和上报网络流量数据，以便将这些数据推送给客户，帮助他们了解优化网络性能的同时提升我们自身的服务质量。
# 二、项目目标
开发一个高效、可靠、安全的流量上报程序，实现以下目标：
1. 实时采集网络流量数据及 mac 等硬件信息。
2. 将采集到的数据上报给客户的同时，一并上报至控制平台进行分析和存储。
3. 确保数据准确性，通过客户提供的上报数据查询 api 去不断对之前上传的数据进行一致性验证。
4. 完全兼容Centos，Ubuntu 等主流 Linux 发行版
5. 确保程序在各种网络环境下的稳定运行。
# 三、程序设计
## 1. 数据源的选择
在上报方式选择上，主要分为以下两种：
- **通过Cacti 采集数据进行上报**
	1. Mac 与cacti 图对应关系的配置维护
	2. Cacti 默认采集的是带宽值，并非总流量值，需要通过更多手段来实现汇总
	3. 数据准确性方面，因为在 cacti 存在端口汇总图的情况下需要通过 OpenCV图文识别的方式获取 cacti图流量值，不能 100%完全保证数据准确性
	4. 如果为了确保准确性，针对 mysql 数据库进行单端口数据获取，那么需要手动对上报程序进行大量配置，维护端口信息
	5. 对于验收中或者异常暂停关闭等情况，无法灵活进行规避
- **通过 Agent 采集数据进行上报**
	1. 在 SkytonOPS 已进行机器纳管的情况下，方便进行统一管理
	2. 自动采集 mac 等硬件信息
	3. 数据准确，支持获取精确的当前总流量值

考虑到我们对机器有归属控制权，综上所述，因此这里**采用 agent 方式上报**，具有方便集中管理和数据准确性上面的绝对优势。
## 2. 功能概述
-主菜单集成在 SkytonOPS，可以在 SkytonOPS 下的“Agent 管理”菜单进行查看和管理
- **控制台（信息概览&全局配置&机器配置）**
	- *推送配置*：配置 access id 、总体数据偏移量、推送失败告警地址等
	- *Agent 状态*：了解当前已部署Agent 程序的所有服务状态，查看在运行的 agent 数量，以及是否存在离线情况
	- *Agent 管理*：考虑非业务期间需要进行规避，因此可以手动对 agent 进行开关状态控制。
	- *源数据处理*：考虑到结算的需要，需要对数据进行进一步处理，允许在数据值的偏移量上做统一或者局部调整。
	- *指定采集接口*：支持指定采集接口
- **推送历史**：对于上报的数据进行记录，需要包含以下信息：
	- 节点名称：与 SkytonOPS 管理平台“主机管理”中的分组列表一致
	- 主机名称：与 SkytonOPS 管理平台“主机管理”中的主机名称一致
	- 推送数据：默认单位字节
	- 推送状态：推送成功还是失败
	- 更新时间：默认格式 YYYY-MM-DD HH:MM:SS
	*也可通过系统“开放平台-厂商上报数据”主动关注上报是否异常*
- **推送失败告警**：对于 3 次以上都未推送成功的，需要进行告警，方便后续人员手动处理

## 3 . 用户界面
用户界面采用和SkytonOPS原本遵循的AntDesign设计风格，做到简洁、美观、明了。
### 3.1 推送配置

![image.png|600](https://pic.yzgsa.com/i/2024/07/10/668e5a0dd1881.png)
### 3.2 全局配置

![image.png|600](https://pic.yzgsa.com/i/2024/07/10/668e59f8306a7.png)

### 3.3 机器采集配置
![image.png|600](https://pic.yzgsa.com/i/2024/07/10/668e5a76b2651.png)

### 3.4 推送历史
![image.png|600](https://pic.yzgsa.com/i/2024/07/10/668e5a571bc2f.png)


### 3.5 Push Agent


![image.png|600](https://pic.yzgsa.com/i/2024/07/10/668e3632abcfa.png)


## 4. 程序主要逻辑
### 4.1 概述
1. 确保每日上报实时流量 (MAC 明细)，每日按小时上报，每 5 分钟一个流量点。
2. 目前默认本机仅一个业务网卡（口），并以此网卡（口）mac 地址为机器唯一标识符进行上报。
4. 验收中，非正式入库的设备不进行上报，可以进行手动控制
5. 如 MAC 更改，及时更改上报，避免双方出现 MAC 差异
6. 规避非业务导致的异常上报
7. 通过可能出现的上报异常进行进一步处理，并通过客户提供的上报数据查询 api 去不断对之前上传的数据进行一致性验证
8. 考虑到结算的需要，需要对数据进行进一步处理，允许在数据值的偏移量上做统一或者局部调整。
### 4.2 采集接口
- 一台只采集一个物理接口，不会采集虚拟接口（bond，br，docker 等）
- 默认采集物理接口为服务器公网管理 ip 所属接口
- 采集接口可以支持在前端页面进行指定

### 4.3 上报字段说明
- {flux_dat}: 上报时间戳
- {flux_hour}：上报时间戳（带小时）
- {provider_id}：厂商标识号
- {provider_uiid}：供应商 uiid
- {isp_id}：运营商 id
- {mac}：mac 地址
- {v 0},{v 1},{v 2},{v 3},{v 4},{v 5},{v 6},{v 7},{v 8},{v 9},{v 10},{v 11}
- {version}：上报数据版本，起始值为数字 1
- {device_type}：设备类型 id
### 4.4 部署脚本
编写Shell 部署脚本
### 4.5. 异常告警
在打开推送开关的情况下，下列情况会进行告警通知：
- 连续 3 次以上未成功推送至客户的的进行告警
- SkytonOPS 连续 3 个周期未接受到 agent数据的主机进行告警（也就是agent 可能离线）

![image.png|600](https://pic.yzgsa.com/i/2024/07/10/668e2e66e12a3.png)

### 5. Api 说明
机器配置 ：`http://1.1.1.13:8999/agent/config/`
全局配置 ：`http://1.1.1.13:8999/agent/get_global_config/`
历史记录 ：`http://1.1.1.13:8999/agent/history/==`

# 四、使用说明
## 1. 部署 Agent
通过 SkytonOPS 模板下的“【部署】PushAgent”来选择对应机器进行部署
![image.png|600](https://pic.yzgsa.com/i/2024/07/11/668f850c40826.png)

## 2. 服务端后台
在服务端启用 agent 数据上报异常以及离线的监控程序
```shell
pyton3 mange.py runcheck
```

![image.png|600](https://pic.yzgsa.com/i/2024/07/11/668f82c8e4b1f.png)


