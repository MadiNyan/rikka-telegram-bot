#!/usr/bin/python
# -*- coding: utf-8 -*-
from telegram.ext.dispatcher import run_async
from telegram import ChatAction, InputMediaPhoto
from telegram.ext import CommandHandler
from modules.logging import log_command
from modules.utils import get_param
from datetime import datetime
import time
import os
import glob
import json
import random
import requests


def module_init(gd):
    global path, files, token
    path = gd.config["path"]
    commands = gd.config["commands"]
    token = gd.full_config["keys"]["telegram_token"]
    for command in commands:
        gd.dp.add_handler(CommandHandler(command, nya))
    files = os.listdir(path)


#@run_async
def nya(bot, update):
    current_time = datetime.strftime(datetime.now(), "%d.%m.%Y %H:%M:%S")
    update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
    amount = get_param(update, 1, 1, 10)
    photos = []
    upload_files = []
    for i in range(amount):
        random_image = random.choice(files)
        attach_name = "".join(random.choice("abcdef1234567890") for x in range(16))
        photos.append({"type": "photo", "media": "attach://" + attach_name})
        upload_files.append((attach_name, (random_image, open(path+random_image, "rb"))))
    requests.post("https://api.telegram.org/bot"+token+"/sendMediaGroup", params={"chat_id": update.message.chat.id, "media": json.dumps(photos)}, files=upload_files)
    print(current_time, ">", "/nya", ">", amount, ">", update.message.from_user.username)
    log_command(bot, update, current_time, "nya")
