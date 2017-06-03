#!/usr/bin/python
# -*- coding: utf-8 -*-
from telegram.ext import CommandHandler
from telegram import ChatAction
from uptime import uptime
import platform
import datetime
import psutil


def handler(dp):
    dp.add_handler(CommandHandler("status", status))


def seconds_to_str(seconds):
    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    return "{} day(s) {:02}:{:02}:{:02}".format(days, hours, minutes, seconds)


def status(bot, update):
    update.message.chat.send_action(ChatAction.TYPING)

    # Uptime
    f = int(uptime())
    pcuptime = seconds_to_str(f)

    uptime_text = "Uptime: ", pcuptime
    uptime_text = "".join(uptime_text)

    # OS
    OS = platform.platform()

    # CPU info
    cpus = psutil.cpu_count(logical=False)
    cpus_log = psutil.cpu_count(logical=True)
    cpu = psutil.cpu_percent(interval=0.5, percpu=True)

    cpu_cores = "CPU cores; physical: ", str(cpus), ", logical: ", str(cpus_log)
    cpu_cores = "".join(cpu_cores)
    cpu_text = "CPU load: ", str(cpu)
    cpu_text = "".join(cpu_text)

    # RAM info
    mem = psutil.virtual_memory()
    total_mem = round(mem[0] / 1024**2)
    used_mem = round(mem[3] / 1024**2)
    # free_mem = round(mem[4] / 1024**2)
    used_mem_perc = round(mem[3] * 100 / mem[0], 1)
    # free_mem_perc = round(mem[4] * 100 / mem[0], 1)

    ram_text = "RAM usage: ", str(used_mem_perc), "% (", str(used_mem), "Mb of ", str(total_mem), "Mb)"
    ram_text = "".join(ram_text)

    # HDD info
    hdd = psutil.disk_usage("/")
    hdd_total = round(hdd[0] / 1024**3, 1)
    hdd_used = round(hdd[1] / 1024**3, 1)
    # hdd_free = round(hdd[2] / 1024**3, 1)
    hdd_perc = hdd[3]

    hdd_text = "HDD usage: ", str(hdd_perc), "% (", str(hdd_used), "Gb of ", str(hdd_total), "Gb)"
    hdd_text = "".join(hdd_text)

    # combine everything
    server_status = "💻 \nOS: " + OS + "\n" + cpu_cores + "\n" + cpu_text + "\n" + ram_text + "\n" + hdd_text + "\n" + uptime_text
    update.message.reply_text(server_status)
    print(datetime.datetime.now(), ">>>", "Done /status", ">>>", update.message.from_user.username)
