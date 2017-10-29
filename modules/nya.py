#!/usr/bin/python
# -*- coding: utf-8 -*-
from telegram.ext.dispatcher import run_async
from telegram.ext import CommandHandler
from modules.logging import log_command
from telegram import ChatAction
from random import randint
from datetime import datetime
import os


def module_init(gd):
    global path, files, filecount
    path = gd.config["path"]
    commands = gd.config["commands"]
    for command in commands:
        gd.dp.add_handler(CommandHandler(command, nya))
    files = os.listdir(path)
    filecount = len(files)
    print("Nya images: ", filecount)


@run_async
def nya(bot, update):
    current_time = datetime.strftime(datetime.now(), "%d.%m.%Y %H:%M:%S")
    update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
    rand = randint(0, filecount-1)
    result = files[rand]
    with open(path+"/"+str(result), "rb") as f:
        update.message.reply_photo(f)
    print(current_time, ">", "/nya", ">", update.message.from_user.username)
    log_command(update, current_time, "nya")