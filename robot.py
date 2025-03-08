# -*- coding: utf-8 -*-
import asyncio
import os
import time
import psutil
import aiohttp
import re
import logging
import multiprocessing
from ping3 import ping  # 只导入 ping 函数
import hashlib
import urllib.parse
import hmac
import base64
import socket  # 新增的模块用于 TCP ping 和端口扫描
from concurrent.futures import ThreadPoolExecutor, as_completed  # 导入线程池
from botpy import logging as botpy_logging
from botpy.client import Client, Intents  # 从 botpy.client 模块导入 Client 和 Intents 类
from botpy.message import Message
from botpy.ext.cog_yaml import read
import platform  # 添加在其他 import 语句附近
import cpuinfo

# 设置日志配置
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # 更改级别为 DEBUG

# 文件输出日志（仅输出到文件，不输出到控制台）
file_handler = logging.FileHandler('robot.log', mode='a', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)  # 更改级别为 DEBUG
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

# 从配置文件读取机器人的信息
test_config = read(os.path.join(os.path.dirname(__file__), "config.yaml"))

# 确保 config.yaml 中包含正确的键
if "appid" not in test_config or "token" not in test_config:
    logger.error("config.yaml 文件中缺少必要的键，请检查配置文件。")
    raise ValueError("config.yaml 文件中缺少必要的键")

API_KEY = test_config["amap"].get("api_key")  # 获取API_KEY
if not API_KEY:
    logger.error("API_KEY未配置，请检查config.yaml文件。")
    raise ValueError("API_KEY未配置")

logger.info(f"读取到的API_KEY: {API_KEY}")

WEATHER_API_URL = "https://restapi.amap.com/v3/weather/weatherInfo"  # 高德天气查询API

# 状态变量
is_running = True

# 添加自动问答词库
auto_responses = {
    "你好": "您好，有什么可以帮您的？",
    "帮我": "请问需要什么帮助呢？",
    "再见": "再见，祝您有美好的一天！"
}

# 定义 start_time 变量
start_time = time.time()  # 记录开始时间

async def get_weather(city):
    """
    异步获取指定城市的天气信息
    :param city: 城市名称
    :return: 包含天气描述、温度等信息的字符串
    """
    params = {
        'city': city,
        'key': API_KEY,
        'output': 'JSON'
    }

    logger.info(f"正在请求天气信息，参数：{params}")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(WEATHER_API_URL, params=params) as response:
                response.raise_for_status()  # 检查请求状态
                data = await response.json()
                if data.get('status') == "1":
                    weather_info = data['lives'][0]
                    city_name = weather_info.get('city')
                    weather_description = weather_info.get('weather')
                    temperature = weather_info.get('temperature')
                    wind_direction = weather_info.get('winddirection')
                    wind_speed = weather_info.get('windspeed')
                    humidity = weather_info.get('humidity')
                    report_time = weather_info.get('reporttime')

                    # 构造回复内容
                    reply_content = (
                        f"{city_name}的天气信息：\n"
                        f"天气状况：{weather_description}\n"
                        f"当前温度：{temperature} °C\n"
                        f"风向：{wind_direction}\n"
                        f"风速：{wind_speed} km/h\n"
                        f"湿度：{humidity}%\n"
                        f"发布时间：{report_time}\n"
                    )
                    return reply_content
                else:
                    return "天气信息获取失败，请检查城市名称或API配置。"
    except aiohttp.ClientError as e:
        logger.error(f"获取天气信息时发生网络错误：{e}")
        return "获取天气信息时发生网络错误，请稍后再试。"
    except Exception as e:
        logger.error(f"获取天气信息时发生错误：{e}")
        return f"天气信息获取出现错误：{e}"

async def tcp_ping(domain, port=80, timeout=2):
    logger.info(f"正在进行 TCP ping 测试，域名：{domain}，端口：{port}")
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            start_time = time.time()
            result = sock.connect_ex((domain, port))  # 尝试连接
            response_time = (time.time() - start_time) * 1000  # 转换为毫秒
             
            if result == 0:  # 连接成功
                return f"TCP连接成功，响应时间：{response_time:.2f} ms"
            else:
                return "无法连接到指定的端口。"
    except Exception as e:
        logger.error(f"进行 TCP 测试时发生错误：{e}")
        return "进行 TCP 测试时发生错误，请检查域名和端口。"

async def port_scan(domain, start_port, end_port):
    logger.info(f"正在进行端口扫描，域名：{domain}，端口范围：{start_port}-{end_port}")
    open_ports = []

    # 定义一个检查单个端口的函数
    def check_port(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.5)
            result = sock.connect_ex((domain, port))
            return port if result == 0 else None

    # 使用线程池来并行检查端口
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = {executor.submit(check_port, port): port for port in range(start_port, end_port + 1)}
        
        for future in as_completed(futures):
            port = futures[future]
            try:
                result = future.result()
                if result is not None:
                    open_ports.append(result)
                    logger.info(f"端口 {result} 是开放的。")
                else:
                    logger.info(f"端口 {port} 是关闭的。")
            except Exception as e:
                logger.error(f"端口 {port} 测试时发生错误：{e}")

    if open_ports:
        return f"开放的端口有：{', '.join(map(str, open_ports))}"
    else:
        return "没有发现开放的端口。"

async def ping_test(domain):
    logger.info(f"正在进行ping测试，域名：{domain}")
    try:
        response_time = ping(domain)  # 进行 ping 测试
        if response_time is not None:
            return f"可以访问，响应时间：{response_time * 1000:.2f} ms"
        else:
            return "无法访问。"
    except Exception as e:
        logger.error(f"进行 ping 测试时发生错误：{e}")
        return "进行 ping 测试时发生错误，请检查域名是否正确。"

def get_system_status():
    try:
        # 获取 CPU 型号名称
        cpu_model = ""
        try:
            with open('/proc/cpuinfo', 'r') as f:
                for line in f:
                    if 'model name' in line:
                        cpu_model = line.split(':')[1].strip()
                        break
        except:
            cpu_model = platform.processor()

        cpu_usage = psutil.cpu_percent(interval=1)
        memory_info = psutil.virtual_memory()
        total_memory = memory_info.total / (1024 * 1024)
        used_memory = memory_info.used / (1024 * 1024)
        memory_usage = (used_memory / total_memory) * 100

        disk_info = psutil.disk_usage('/')
        total_disk = disk_info.total / (1024 * 1024 * 1024)
        used_disk = disk_info.used / (1024 * 1024 * 1024)
        disk_usage = (used_disk / total_disk) * 100
        
        # 获取系统信息
        system_info = {
            'system': platform.system(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': cpu_model,  # 使用从 /proc/cpuinfo 读取的 CPU 信息
            'cpu_cores': psutil.cpu_count(logical=False),  # 物理核心数
            'cpu_threads': psutil.cpu_count(logical=True)  # 逻辑核心数
        }
        
        # 计算运行时间
        total_seconds = time.time() - start_time
        days = total_seconds // (24 * 3600)
        hours = (total_seconds % (24 * 3600)) // 3600
        minutes = (total_seconds % (24 * 3600) % 3600) // 60
        seconds = total_seconds % 60

        return cpu_usage, memory_usage, disk_usage, (days, hours, minutes, seconds), system_info
    except Exception as e:
        logger.error(f"获取系统状态时发生错误：{e}")
        return None, None, None, None, None

# 自定义客户端类
class MyClient(Client):
    async def on_ready(self):
        logger.info(f"机器人 「{self.robot.name}」 on_ready!")

    async def on_at_message_create(self, message: Message):
        logger.info(message.author.avatar)
        if "sleep" in message.content:
            await asyncio.sleep(10)
        logger.info(message.author.username)

        # 处理消息内容，去掉@用户部分
        content = re.sub(r'<@!?\d+>', '', message.content).strip()
        logger.info(f"收到消息：{content}")  # 记录收到的消息

        # 去掉前缀 /
        if content.startswith("/"):
            content = content[1:].strip()

        global is_running
        reply_content = ""
        # 在 MyClient 类的 on_at_message_create 方法中修改运行状态的处理部分
        # 在 MyClient 类中修改显示部分
        if content == "运行状态":
            cpu_usage, memory_usage, disk_usage, runtime, system_info = get_system_status()
            if cpu_usage is not None:  # 确保状态正常
                days, hours, minutes, seconds = runtime
                reply_content = (
                    f"当前状态：运行中\n"
                    f"系统信息：{system_info['system']} {system_info['version']}\n"
                    f"处理器：{system_info['processor']}\n"
                    f"核心数：{system_info['cpu_cores']}核心{system_info['cpu_threads']}线程\n"
                    f"处理器架构：{system_info['machine']}\n"
                    f"CPU占用：{cpu_usage}%\n"
                    f"内存占用：{memory_usage:.2f}%\n"
                    f"存储占用：{disk_usage:.2f}%\n"
                    f"总运行时间：{int(days)}天 {int(hours)}小时 {int(minutes)}分钟 {seconds:.2f}秒"
                )
                logger.info("回复运行状态请求")
            else:
                reply_content = "获取系统状态时发生错误。"
        elif content.startswith("天气"):
            city = content[len("天气"):].strip()
            if city:
                reply_content = await get_weather(city)
                logger.info(f"回复天气请求：{reply_content}")
            else:
                reply_content = "格式不正确，请使用：天气 <城市名>"
                logger.warning(f"天气请求格式不正确：{content}")
        elif content.startswith("ping"):
            domain = content[len("ping"):].strip()  # 获取域名
            if domain:
                reply_content = await ping_test(domain)
                logger.info(f"回复 ping 请求：{reply_content}")
            else:
                reply_content = "格式不正确，请使用：ping <域名>"
                logger.warning(f"ping 请求格式不正确：{content}")
        elif content.startswith("tcping"):
            parts = content.split()
            domain = parts[1] if len(parts) > 1 else ''
            port = int(parts[2]) if len(parts) > 2 else 80  # 默认端口为 80
            if domain:
                reply_content = await tcp_ping(domain, port)
                logger.info(f"回复 tcp_ping 请求：{reply_content}")
            else:
                reply_content = "格式不正确，请使用：tcping <域名> [<端口>]"
                logger.warning(f"tcping 请求格式不正确：{content}")
        elif content.startswith("端口测试"):
            parts = content.split()
            domain = parts[1] if len(parts) > 1 else ''
            start_port = int(parts[2]) if len(parts) > 2 else 1  # 默认起始端口为 1
            end_port = int(parts[3]) if len(parts) > 3 else 1024  # 默认结束端口为 1024
            
            if domain:
                reply_content = await port_scan(domain, start_port, end_port)
                logger.info(f"回复端口测试请求：{reply_content}")
            else:
                reply_content = "格式不正确，请使用：端口测试 <域名> [<起始端口>] [<结束端口>]"
                logger.warning(f"端口测试请求格式不正确：{content}")
        elif content.startswith("端口扫描"):
            parts = content.split()
            domain = parts[1] if len(parts) > 1 else ''
            start_port = int(parts[2]) if len(parts) > 2 else 1  # 默认起始端口为 1
            end_port = int(parts[3]) if len(parts) > 3 else 1024  # 默认结束端口为 1024
            
            if domain:
                reply_content = await port_scan(domain, start_port, end_port)
                logger.info(f"回复端口扫描请求：{reply_content}")
            else:
                reply_content = "格式不正确，请使用：端口扫描 <域名> <起始端口> <结束端口>"
                logger.warning(f"端口扫描请求格式不正确：{content}")
        else:
            reply_content = "我不太明白你说的是什么..."
            logger.warning(f"无法理解的请求：{content}")

        # 回复消息
        if reply_content:
            await message.reply(content=reply_content)

def run_bot():
    """运行机器人，作为守护进程"""
    logger.info("机器人启动中...")
    # 通过kwargs，设置需要监听的事件通道
    intents = Intents(public_guild_messages=True)
    client = MyClient(intents=intents)
    client.run(appid=test_config["appid"], secret=test_config["token"])

if __name__ == "__main__":
    # 创建并启动守护进程
    bot_process = multiprocessing.Process(target=run_bot)
    bot_process.daemon = True  # 设置为守护进程
    bot_process.start()

    try:
        while True:
            time.sleep(1)  # 维持主程序的运行
    except KeyboardInterrupt:
        logger.info("程序被手动终止。")
