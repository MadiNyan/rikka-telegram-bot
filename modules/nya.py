#!/usr/bin/python
# -*- coding: utf-8 -*-
from telegram.ext.dispatcher import run_async
from telegram.ext import CommandHandler
from telegram import ChatAction
from random import randint
import datetime
import yaml
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
    update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
    rand = randint(0, filecount-1)
    result = files[rand]
    with open(path+"/"+str(result), "rb") as f:
        update.message.reply_photo(f)
    print(datetime.datetime.now(), ">>>", "Sent nya", ">>>", update.message.from_user.username)
