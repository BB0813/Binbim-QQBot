#!/bin/bash

# 更新包列表
sudo yum update -y

# 安装Python3和pip3
sudo yum install -y python3 python3-pip

# 安装requirements.txt中的依赖库
pip3 install -r requirements.txt