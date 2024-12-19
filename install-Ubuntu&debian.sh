#!/bin/bash

# 更新包列表
sudo apt update

# 安装Python3和pip3
sudo apt install -y python3 python3-pip

# 安装requirements.txt中的依赖库
pip3 install -r requirements.txt
