#!/usr/bin/python
# -*- coding: utf-8 -*-
from modules.utils import caption_filter, get_image, send_image, get_param
from telegram.ext import CommandHandler, MessageHandler
from modules.logging import log_command
from telegram import ChatAction
from datetime import datetime
from PIL import Image
import os


def module_init(gd):
    global path, extensions
    path = gd.config["path"]
    extensions = gd.config["extensions"]
    commands = gd.config["commands"]
    for command in commands:
        gd.dp.add_handler(MessageHandler(caption_filter("/"+command), jpeg))
        gd.dp.add_handler(CommandHandler(command, jpeg))


def jpeg(bot, update):
    current_time = datetime.strftime(datetime.now(), "%d.%m.%Y %H:%M:%S")
    filename = datetime.now().strftime("%d%m%y-%H%M%S%f")
    compress = get_param(update, 6, 1, 10)
    if compress is None:
        return
    else:
        compress = 11 - compress
    try:
        extension = get_image(bot, update, path, filename)
    except:
        update.message.reply_text("I can't get the image! :(")
        return
    update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
    if extension not in extensions:
        update.message.reply_text("Unsupported file, onii-chan!")
        return

    original = Image.open(path+filename+extension, 'r')
    if extension == ".jpg":
        original.save(path+filename+".jpg",quality=compress,optimize=True)
    else:
        rgb_im = original.convert('RGB')
        rgb_im.save(path+"compressed.jpg",quality=compress,optimize=True)
        foreground = Image.open(path+"compressed.jpg")
        try:
            original.paste(foreground, (0, 0), original)
        except:
            pass  
        original.save(path+filename+extension)
        os.remove(path+"compressed.jpg")
    send_image(update, path, filename, extension)
    os.remove(path+filename+extension)
    print (current_time, ">", "/jpeg", ">", update.message.from_user.username)
    log_command(bot, update, current_time, "jpeg")
