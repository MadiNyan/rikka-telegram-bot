#!/usr/bin/python
# -*- coding: utf-8 -*-
from modules.logging import logging_decorator
from telegram.ext import MessageHandler, PrefixHandler
from modules.utils import get_image, Caption_Filter
from datetime import datetime
from telegram import ChatAction
from random import randint
import subprocess
import os


def module_init(gd):
    global path, extensions
    path = gd.config["path"]
    extensions = gd.config["extensions"]
    commands = gd.config["commands"]
    for command in commands:
        caption_filter = Caption_Filter("/"+command)
        gd.dp.add_handler(MessageHandler(caption_filter, glitch))
        gd.dp.add_handler(PrefixHandler("/", command, glitch))


@logging_decorator("glitch")
def glitch(update, context):
    filename = datetime.now().strftime("%d%m%y-%H%M%S%f")
    try:
        extension = get_image(update, context, path, filename)
    except:
        update.message.reply_text("I can't get the image! :(")
        return
    update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
    if extension not in extensions:
        update.message.reply_text("Unsupported file, onii-chan!")
        return False
    jpg = "convert " + path + filename + extension + " -resize 100% " + path + filename + ".jpg"
    subprocess.run(jpg, shell=True)
    process_img(update, filename)
    os.remove(path+filename+extension)
    os.remove(path+filename+"-glitched.jpg")


def process_img(update, filename):
    with open(path + filename + ".jpg", "rb") as f:
        linelist = list(f)
        linecount = len(linelist) - 10
        for i in range(5):
            i = randint(1, linecount - 1)
            linecount = linecount - 1
            del linelist[i]
    with open(path + filename + "-glitched" + ".jpg", "wb") as f:
        for content in linelist:
            f.write(content)
    with open(path + filename + "-glitched" + ".jpg", "rb") as f:
        update.message.reply_photo(f)
