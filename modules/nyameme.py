#!/usr/bin/python
# -*- coding: utf-8 -*-
from modules.utils import get_image
from modules.logging import logging_decorator
from telegram.ext import PrefixHandler
from telegram.ext.dispatcher import run_async
from modules.memegenerator import make_meme
from telegram import ChatAction
from datetime import datetime
import random
import shutil
import os


def module_init(gd):
    global path, extensions, fonts_dict, nyapath, files
    path = gd.config["path"]
    extensions = gd.config["extensions"]
    commands = gd.config["commands"]
    fonts_dict = {}
    nyapath = gd.config["nyapath"]
    files = os.listdir(nyapath)
    for i in gd.config["fonts"]:
        fonts_dict[gd.config["fonts"][i]["name"]] = gd.config["fonts"][i]["path"]
    for command in commands:
        gd.dp.add_handler(PrefixHandler("/", commands, nyameme))


@run_async
@logging_decorator("nyameme")
def nyameme(update, context):
    filename = datetime.now().strftime("%d%m%y-%H%M%S%f")
    reply = update.message.reply_to_message
    if reply:
        if reply.caption:
            args = reply.caption
        elif reply.text:
            args = reply.text
        else:
            args = " ".join(context.args)
        args = args.split(" ")
    else:
        args = context.args
    if len(args) < 1:
        update.message.reply_text("Type in some text!")
        return
    if len(args) == 1:
        top_text = None
        bottom_text = args[0]
    else:
        split_spot = random.randint(1, len(args)-1)
        top_text = " ".join(args[:split_spot])
        bottom_text = " ".join(args[split_spot:])
    rand_font = random.choice(list(fonts_dict))
    font = fonts_dict[rand_font]
    random_image = random.choice(files)
    filename = random_image.split(".")[0]
    extension = "."+random_image.split(".")[1]
    if extension not in extensions:
        update.message.reply_text("Unexpected error")
        return
    shutil.copy(nyapath+random_image, path+random_image)
    make_meme(top_text, bottom_text, filename, extension, path, font)
    update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
    with open(path + filename+"-meme" + extension, "rb") as f:
        update.message.reply_photo(f)
    os.remove(path+filename+extension)
    os.remove(path+filename+"-meme"+extension)
