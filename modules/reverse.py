#!/usr/bin/python
# -*- coding: utf-8 -*-
from modules.utils import get_image, send_image
from modules.logging import logging_decorator
from telegram.ext import PrefixHandler, MessageHandler
from telegram.ext.dispatcher import run_async
from telegram import ChatAction
from datetime import datetime
import subprocess
import os


def module_init(gd):
    global path
    path = gd.config["path"]
    commands = gd.config["commands"]
    for command in commands:
        gd.dp.add_handler(MessageHandler(caption_filter, reverse))
        gd.dp.add_handler(PrefixHandler("/", command, reverse))


@run_async
@logging_decorator("reverse")
def reverse(update, context):
    filename = datetime.now().strftime("%d%m%y-%H%M%S%f")
    try:
        extension = get_image(update, context, path, filename)
    except:
        update.message.reply_text("Can't get the video")
        return
    update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
    video = reverse_video(path, filename, extension)
    send_image(update, path, video, extension)
    os.remove(path+filename+extension)
    os.remove(path+video+extension)


def reverse_video(path, filename, extension):
    new_name = "reversed"
    print(path + filename + extension)
    args = "ffmpeg -loglevel panic -i " + path + filename + extension + " -vf reverse -af areverse " + path + "reversed" + extension + " -y"
    subprocess.run(args, shell=True) 
    return new_name