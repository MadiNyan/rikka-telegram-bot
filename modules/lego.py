#!/usr/bin/python
# -*- coding: utf-8 -*-
from modules.utils import Caption_Filter, get_image, send_image, get_param
from modules.logging import logging_decorator
from telegram.ext import PrefixHandler, MessageHandler
from telegram.ext.dispatcher import run_async
from telegram import ChatAction
from datetime import datetime
import subprocess
import legofy
import os


def module_init(gd):
    global path, extensions
    path = gd.config["path"]
    extensions = gd.config["extensions"]
    commands = gd.config["commands"]
    for command in commands:
        caption_filter = Caption_Filter("/"+command)
        gd.dp.add_handler(MessageHandler(caption_filter, lego))
        gd.dp.add_handler(PrefixHandler("/", command, lego))


@run_async
@logging_decorator("lego")
def lego(update, context):
    filename = datetime.now().strftime("%d%m%y-%H%M%S%f")
    size = get_param(update, 50, 1, 100)
    if size is None:
        return
    try:
        extension = get_image(update, context, path, filename)
    except:
        update.message.reply_text("Can't get the image! :(")
        return
    if extension not in extensions:
        update.message.reply_text("Unsupported file, onii-chan!")
        return False
    update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
    if extension == ".webp" or ".png":
        stick = "convert " + path + filename + extension + " -background white -flatten " + path + filename + extension
        subprocess.run(stick, shell=True)
    legofy.main(image_path=path + filename + extension,
                output_path=path + filename + "-lego" + extension,
                size=size, palette_mode=None, dither=False)
    send_image(update, path, filename+"-lego", extension)
    os.remove(path+filename+extension)
    os.remove(path+filename+"-lego"+extension)
