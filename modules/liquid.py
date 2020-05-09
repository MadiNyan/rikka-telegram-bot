#!/usr/bin/python
# -*- coding: utf-8 -*-
from modules.utils import caption_filter, get_param, get_image, send_image
from modules.logging import logging_decorator
from telegram.ext import CommandHandler, MessageHandler
from telegram.ext.dispatcher import run_async
from telegram import ChatAction
from datetime import datetime
from wand.image import Image
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
    power = get_param(update, 60, -100, 100)
    if power is None:
        return
    try:
        extension = get_image(bot, update, path, filename)
    except:
        update.message.reply_text("I can't get the image! :(")
        return
    power = (100 - (power / 1.3)) / 100
    update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
    with Image(filename=path+filename+extension) as original:
        w, h = original.size
        new = Image()
        for i in range(len(original.sequence)):
            with original.sequence[i] as frame: 
                img = Image(image=frame)
            img.liquid_rescale(int(w*power), int(h*power), delta_x =1)
            img.resize(w, h)
            new.sequence.append(img)
        new.save(filename=path+filename+extension)
        send_image(update, path, filename, extension)
        new.close()
        os.remove(path+filename+extension)
