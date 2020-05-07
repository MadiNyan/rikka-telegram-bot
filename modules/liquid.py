#!/usr/bin/python
# -*- coding: utf-8 -*-
from modules.utils import caption_filter, get_image, send_image, get_param
from modules.logging import logging_decorator
from telegram.ext import CommandHandler, MessageHandler
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
        gd.dp.add_handler(MessageHandler(caption_filter("/"+command), liquid))
        gd.dp.add_handler(CommandHandler(command, liquid))


@run_async
@logging_decorator("liq")
def liquid(bot, update):
    filename = datetime.now().strftime("%d%m%y-%H%M%S%f")
    power = get_param(update, 60, 1, 100)
    if power is None:
        return
    try:
        extension = get_image(bot, update, path, filename)
    except:
        update.message.reply_text("I can't get the image! :(")
        return
    update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
    identify = subprocess.Popen("identify " + path + filename + extension, stdout=subprocess.PIPE).communicate()[0]
    res = str(identify.split()[2])[2:-1]
    size = str(100 - (power / 1.3))
    name = filename + "-liquid"
    x = "convert " + path + filename + extension + " -liquid-rescale " + \
         size + "%x" + size + "% -resize " + res + "! " + path + name + extension
    subprocess.run(x, shell=True)
    if extension == ".mp4":
        mp4fix = "ffmpeg -loglevel panic -i " + path + name + extension + \
                  " -an -vf scale=trunc(iw/2)*2:trunc(ih/2)*2 \
                  -pix_fmt yuv420p -c:v libx264 -profile:v high -level:v 2.0 " \
                  + path + name + "_mp4" + extension + " -y"
        subprocess.run(mp4fix, shell=True)
        os.remove(path+name+extension)
        name = name + "_mp4"
    send_image(update, path, name, extension)
    os.remove(path+filename+extension)
    os.remove(path+name+extension)
