#!/usr/bin/python
# -*- coding: utf-8 -*-
from telegram.ext import CommandHandler, MessageHandler
from modules.custom_filters import caption_filter
from modules.get_image import get_image
from telegram import ChatAction
from random import randint
import datetime
import yaml


def handler(dp):
    dp.add_handler(MessageHandler(caption_filter("/glitch"), glitch))
    dp.add_handler(CommandHandler("glitch", glitch))

# import path
with open("config.yml", "r") as f:
    glitch_folder = yaml.load(f)["path"]["glitch"]


# get image, then glitch
def glitch(bot, update):
    try:
        get_image(bot, update, glitch_folder)
    except:
        update.message.reply_text("I can't get the image! :(")
        return
    update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
    process_img(update)


# glitch processing; deleting lines in .jpg file
def process_img(update):
    with open(glitch_folder + "original.jpg", "rb") as f:
        linelist = list(f)
        linecount = len(linelist) - 10
        for i in range(5):
            i = randint(1, linecount - 1)
            linecount = linecount - 1
            del linelist[i]
    with open(glitch_folder + "result.jpg", "wb") as f:
        for content in linelist:
            f.write(content)
    with open(glitch_folder + "result.jpg", "rb") as f:
        update.message.reply_photo(f)
    print (datetime.datetime.now(), ">>>", "Done glitching", ">>>",
           update.message.from_user.username)
