#!/bin/bash

# 更新包管理器
sudo yum update -y

# 安装必要的开发工具
sudo yum groupinstall "Development Tools" -y

# 安装 Python 和 pip（如果尚未安装）
sudo yum install python3 python3-pip -y

# 安装必要的 Python 库
pip3 install -r requirements.txt

echo "所有库已成功安装！"
