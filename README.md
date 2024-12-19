# Binbim-QQbot 项目说明
# 已恢复正常功能 库已迁移完成 可正常使用
## 项目简介
Binbim-QQbot 是一款基于 Python 语言的 QQ 机器人框架，使用 aiohttp 库实现了 QQ 官方协议的 HTTP API 接口，并使用 psutil 库实现了系统监控功能。

## 项目特点
> 轻量化：框架仅依赖 aiohttp、psutil 库，无需安装额外的依赖库，可直接部署运行。

> 易于使用：提供了丰富的 API，可以快速实现 QQ 机器人的功能。

> 功能丰富：提供了丰富的插件接口，可以灵活地扩展机器人的功能。

> 系统监控：提供了系统监控功能，可以实时查看机器人的运行状态。

## 项目依赖
> Python 3.x 及以上版本

> aiohttp 库

> psutil 库

> qqbot 库

## 项目结构
Binbim-QQBot/
│
├── robot.py                # 主程序文件
├── config.yaml             # 配置文件，包含API_KEY等信息
├── README.md            #项目配置教程文件
├── robot.log               # 日志文件
├── install-CentOS.sh    #依赖库一键安装脚本（CentOS版）
├── install-Ubuntu-and-debian.sh    #依赖库一键安装脚本（Ubuntu&debian版）
└── 


## 项目使用
> 下载项目代码

> 使用一键脚本安装依赖库

> 配置 config.yaml 文件

> 启动机器人

## 项目更新日志
> 2024.11.5：发布 1.0 版本。

> 2024.11.8：发布 1.1 版本 本次更新仅补充部署教程及维修部分BUG 因新架构出现巨大问题 正在重构项目所有源码

> 2024.12.17 发布V0.0.1Beta版本 本次更新将代码完全重构

> 2024.12.19 发布V0.0.2Beta版本 本次更新重新编写了依赖库安装脚本 并修复了部分BUG

## 后续将会逐步增加功能以及新项目 求各位给个 Star
## 本项目已增加 Apache-2.0 开源协议

> **联系方式**
>> 个人主页: `https://home.binbim.asia/`

>> 个人blog:（暂无法访问） `https://xfast.firefun.cn/`

>> 邮箱: `binbim@binbim.asia`

>> QQ 群组: `619925543`

>> Telegram 频道: `@binbimasia`

>> GitHub: `https://github.com/BB0813`

# Binbim-QQBot框架部署说明：在 Linux 服务器上静默运行 Python 机器人
## 一. 环境准备
> 确保你的服务器上安装了 Python 3.x 及以上版本 可以通过以下命令检查：

```bash
python3 --version
```

> 安装项目所需的 Python 包，使用以下命令：

```bash
./install-对应Linux系统名字.sh
如：./install-CentOS.sh
```

> 确保你的 requirements.txt 文件中包含了 aiohttp、psutil 和 qq-bot 等必需库。

## 二. 代码部署
> 上传代码 将 robot.py 和 config.yaml 文件上传到你的 Linux 服务器中，通常位置可以放在 /home/user/QQbot/ 目录下。

> 权限设置 为 robot.py 文件添加可执行权限，运行：

```bash
chmod +x robot.py
```

## 三. 静默运行
> 1. 使用 nohup 命令
>> 可以使用 nohup 命令将 Python 脚本放在后台运行，即使关闭终端也会继续运行。

> 打开终端，进入程序目录，然后执行以下命令：

```bash
nohup python3 robot.py > robot.log 2>&1 &
```

>> nohup：不挂断运行，即使退出终端也不会停止程序。

>> python3 robot.py：执行你的 Python 脚本。

>> (> robot.log)：将标准输出重定向到 robot.log 文件中。

>> (2>&1)：将错误输出也重定向到 robot.log 文件中。

>> (&)：将程序放入后台运行。

## 四. 查看日志内容
> 查看实时日志 可以使用 tail 命令查看 robot.log 文件，获取实时日志输出：

 ```bash
tail -f robot.log
```

> 查看历史日志 使用 cat 命令查看全部日志：

```bash
cat robot.log
```

> 使用 less 查看 命令也可以使用 less 进行简单的分页查看，非常方便：
```bash
less robot.log
```

## 五. 停止运行
> 如果需要停止后台运行的进程，可以使用以下命令查找进程 ID（PID）并 kill 进程：

```bash
ps aux | grep robot.py
找到对应的 PID 后，使用命令：
kill <PID>
```

## 总结
> 通过上述步骤，你可以在 Linux 服务器上成功部署你的 Python 机器人程序，使其静默运行并能够方便地查看日志内容。确保定期检查日志文件以监控机器人的运行状态和性能。