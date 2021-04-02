#!/usr/bin/python
# -*- coding: utf-8 -*-
from modules.logging import logging_decorator
from telegram.ext import PrefixHandler
from telegram import ChatAction
from datetime import datetime
from uptime import uptime
import platform
import cpuinfo
import psutil


def module_init(gd):
    commands = gd.config["commands"]
    for command in commands:
        gd.dp.add_handler(PrefixHandler("/", command, system))


def get_size(bytes, suffix="B"):
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor


def seconds_to_str(seconds):
    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    return "{} day(s), {:02} hours, {:02} minutes, {:02} seconds".format(days, hours, minutes, seconds)


@logging_decorator("system")
def system(update, context):
    update.message.chat.send_action(ChatAction.TYPING)

    # System information
    uname = platform.uname()
    a = "="*10, " 💻 System Info ", "="*9
    sys_header = "".join(a)
    sys_info = "{}\n\nSystem: {}\nNode Name: {}\nVersion: {}\n".format(sys_header, uname.system, uname.node, uname.version)

    # Uptime
    b = "="*14, " Uptime ", "="*13
    upt_header = "".join(b)
    f = int(uptime())
    pcuptime = seconds_to_str(f)
    up = "{}\n\nUptime: {}\n".format(upt_header, pcuptime)

    # CPU information
    c = "="*15, " CPU ", "="*15
    cpu_header = "".join(c)
    cpumodel = cpuinfo.get_cpu_info()['brand_raw']
    cpufreq = psutil.cpu_freq()
    cpu_info = "{}\n\n{}\nPhysical cores: {}\nTotal cores: {}\nMax Frequency: {:.2f} Mhz\nCurrent Frequency: {:.2f} Mhz\nCPU Usage: {}%\n".format(
                cpu_header, cpumodel, psutil.cpu_count(logical=False), psutil.cpu_count(logical=True), cpufreq.max, cpufreq.current, psutil.cpu_percent(percpu=False, interval=1))

    # RAM Information
    d = "="*15, " RAM ", "="*15
    ram_header = "".join(d)
    svmem = psutil.virtual_memory()

    ram_info = "{}\n\nTotal: {}\nAvailable: {} ({:.2f}%)\nUsed: {} ({:.2f}%)\n".format(
                ram_header, get_size(svmem.total), get_size(svmem.available), 100-svmem.percent, get_size(svmem.used), svmem.percent)

    # HDD Information
    e = "="*15, " HDD ", "="*15, "\n"
    hdd_header = "".join(e)
    hdd_info = hdd_header
    partitions = psutil.disk_partitions()
    for partition in partitions:
        try:
            partition_usage = psutil.disk_usage(partition.mountpoint)
        except PermissionError:
            continue
        disk_info = "\nDevice: {}\nFile system: {}\nTotal Size: {}\nUsed: {} ({:.2f}%)\nFree: {} ({:.2f}%)\n".format(
                    partition.device, partition.fstype, get_size(partition_usage.total), 
                    get_size(partition_usage.used), partition_usage.percent, get_size(partition_usage.free), 
                    100-partition_usage.percent)
        hdd_info = "{}{}".format(hdd_info, disk_info)

    # Combine everything
    server_status = "```\n{}\n{}\n{}\n{}\n{}\n```".format(sys_info, up, cpu_info, ram_info, hdd_info)
    update.message.reply_text(server_status, parse_mode="Markdown")
