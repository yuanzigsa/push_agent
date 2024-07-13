#!/bin/bash
#===============================================================================
# Date：July. 13th, 2024
# Author : yuanzi
# Website: https://www.yzgsa.com
# Description: 初始化系统，提供pushAgent运行环境+TX业务运行环境
#===============================================================================


# 定义日志函数
get_current_time() {
    echo "$(date "+%Y-%m-%d %H:%M:%S")"
}
log_info() {
    echo -e "$(get_current_time) \e[32mINFO\e[0m: $1"
}

log_error() {
    echo -e "$(get_current_time) \e[31mERROR\e[0m: $1"
}

log_warning() {
    echo -e "$(get_current_time) \e[33mWARNING\e[0m: $1"
}

log_info "执行开始..."
# 检查是否以root用户身份运行
if [[ $EUID -ne 0 ]]; then
    log_error "请以root用户身份运行此脚本"
    exit 1
fi

# 校准时间
check_time() {
    log_info "校准时间..."
    yum install -y ntpdate &> /dev/null
    ntpdate time.windows.com &> /dev/null
    timedatectl set-timezone Asia/Shanghai &> /dev/null
    hwclock --systohc &> /dev/null
    log_info "已校准系统时间"
}

# 配置DNS确保正确解析域名
check_configure_dns() {
    log_info "检测和配置DNS..."
    if ! grep -E '^nameserver' '/etc/resolv.conf' &> /dev/null; then
        echo -e "nameserver 114.114.114.114\nnameserver 8.8.8.8" >> /etc/resolv.conf
        log_info "DNS已配置为114.114.114.114和8.8.8.8"
    fi
    sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config
}

install_package() {
    local package=$1
    log_info "安装${package}..."
    yum install -y "${package}" &> /dev/null
    log_info "${package}已安装"
}

install_software() {
    install_package "yum-fastestmirror"
    install_package "net-tools"
    install_package "gcc python3-devel"
    install_package "wget"
    install_package "git"
}

# python3环境部署及所需外置库的安装
install_python3_env() {
    install_package "python3"

    log_info "安装python所需的外置库..."
    pip3 install requests psutil colorlog -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn &> /dev/null
    log_info "python所需的外置库已全部安装"
}

# 创建服务并运行
create_systemd_service() {
    script_path="/opt/push_agent/main.py"
    log_info "创建push_agent.py脚本并写进系统服务运行..."
    service_content="[Unit]\nDescription=PushAgent\nAfter=network.target\n\n[Service]\nExecStart=/usr/bin/python3 $script_path\nRestart=always\nKillMode=process\nUser=root\nWorkingDirectory=/opt/push_agent\n\n[Install]\nWantedBy=multi-user.target\n"
    service_file_path='/etc/systemd/system/push_agent.service'
    echo -e "$service_content" > "$service_file_path"

    systemctl daemon-reload &> /dev/null
    systemctl enable push_agent.service &> /dev/null
    systemctl start push_agent.service &> /dev/null
    log_info "PushAgent程序已创建并写进系统服务并设置成开机自启"
}

# 部署push_agent程序
deploy_push_agent() {
    # 下载agent
    mkdir -p /opt/
    path="/opt/push_agent"

    if [ -d "$path" ]; then
        log_info "PushAgent程序已存在，正在更新..."
        cd /opt/push_agent
        git stash save --include-untracked || true
        git stash drop || true
        git pull
        service push_agent restart
        log_info "PushAgent程序已经更新重启！"
    else
        log_warning "PushAgent程序不存在，正在部署..."
        cd /opt/ && git clone "$PROJECT_URL"
        log_info "PushAgent程序下载完成"
    fi

    mkdir -p /opt/push_agent/config /opt/push_agent/log

    config=$(echo "$config_template" | sed "s/__MACHINE_ID__/$SPUG_HOST_ID/" | sed "s/__MACHINE_IP__/$SPUG_HOST_HOSTNAME/")
    echo "$config" > /opt/push_agent/config/config.json

    # 安装基础环境
    install_python3_env
    create_systemd_service
}

deploy_TX_env() {
    log_info "开始部署TX业务环境..."
    # 创建挂载点目录
    log_info "创建挂载点目录..."
    mkdir -p /pcdn_data_hdd /etc/pcdn /pcdn_data/storage{1..4}_ssd /pcdn_data_hdd/storage{1..8}_hdd
    touch /etc/pcdn/pcdn.conf

    MAC=$(ifconfig $(ip ro get 114.114.114.114 | awk '{print $5;exit}') | awk '/ether/ {print $2}')
    echo "macs  $MAC" >> /etc/pcdn/pcdn.conf
    echo "nics  eth0" >> /etc/pcdn/pcdn.conf

    log_info "开始下载安装包..."
    wget http://120.233.19.189:9080/installer-0.7.23.tar.gz
    tar -zvxf installer-0.7.23.tar.gz
    yum -y install http://120.233.19.189:9080/kernel-5.4.119-19.0006.tl2.x86_64.rpm &> /dev/null
    grub2-set-default 'CentOS Linux (5.4.119-19-0006) 7 (Core)'

    DEVICE=$(lsblk -d -o NAME | grep -v sda | grep -v NAME | sort)
    for DEV in $DEVICE; do
        parted -s  "/dev/$DEV" mklabel gpt
        parted -s "/dev/$DEV" mkpart primary 0% 100%
        sleep 2
        if [[ $DEV =~ nvme ]]; then
            /usr/sbin/mkfs.xfs  -f  "/dev/${DEV}p1"
        else
            /usr/sbin/mkfs.xfs  -f  "/dev/${DEV}1"
        fi
    done

    ssd=$(blkid -s UUID | grep "$DEVICE" | grep nvme | awk '{gsub(/"/,""); print $2}')
    hdd=$(blkid -s UUID | grep "$DEVICE" | grep -v sda  |grep sd | awk '{gsub(/"/,""); print $2}')
    count=1
    for ssd in $ssd; do
        echo "$ssd  /pcdn_data/storage${count}_ssd  xfs defaults 0 0" >> /etc/fstab
        count=$((count + 1))
    done

    count=1
    for hdd in $hdd; do
        echo "$hdd  /pcdn_data_hdd/storage${count}_hdd  xfs defaults 0 0" >> /etc/fstab
        count=$((count + 1))
    done

    OLD_NAME=$(ip ro get 114.114.114.114 | awk '{print $5;exit}')
    INTERFACE_NAME="eth0"
    if [ ! -f "/etc/udev/rules.d/70-persistent-net.rules" ]; then
        touch /etc/udev/rules.d/70-persistent-net.rules
    fi
    mac=$(cat /sys/class/net/${OLD_NAME}/address)
    echo "SUBSYSTEM==\"net\", ACTION==\"add\", DRIVERS==\"?*\", ATTR{address}==\"${mac}\", ATTR{dev_id}==\"0x0\", ATTR{type}==\"1\", NAME=\"${INTERFACE_NAME}\"" > /etc/udev/rules.d/70-persistent-net.rules
    cp /etc/sysconfig/network-scripts/ifcfg-${OLD_NAME} /etc/sysconfig/network-scripts/ifcfg-${OLD_NAME}.bak
    sed -i "s/${OLD_NAME}/${INTERFACE_NAME}/g" /etc/sysconfig/network-scripts/ifcfg-${OLD_NAME}
    mv /etc/sysconfig/network-scripts/ifcfg-${OLD_NAME} /etc/sysconfig/network-scripts/ifcfg-${INTERFACE_NAME}
    mount -a

    log_info "TX业务运行环境初始化完成"
}

start() {
    check_configure_dns
    check_time
    install_software
    deploy_TX_env
    deploy_push_agent
    sleep 2
    systemctl status push_agent.service
}

PROJECT_URL="https://gitee.com/yzgsa/push_agent.git"
config_template='{
  "machine_id": "__MACHINE_ID__",
  "machine_ip": "__MACHINE_IP__",
  "config_api":"http://xxx.xxx.xxx.xxx:8888/agent/config/",
  "global_config_api":"http://xxx.xxx.xxx.xxx:8888/agent/get_global_config/",
  "history_api":"http://xxx.xxx.xxx.xxx:8888/agent/history/",
  "access_token": "******************************"
}'

start

