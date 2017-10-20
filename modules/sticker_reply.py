#!/usr/bin/python
# -*- coding: utf-8 -*-
from telegram.ext import MessageHandler, Filters
import datetime

def module_init(gd):
    global keywords, sticker_path
    keywords = gd.config["keywords"]
    sticker_path = gd.config["sticker_path"]
    gd.dp.add_handler(MessageHandler(Filters.text, sticker_rep))


def sticker_rep(bot, update):
    for word in keywords:
        if word in update.message.text:
            with open(sticker_path, "rb") as sticker:
                update.message.reply_sticker(sticker)
            print(datetime.datetime.now(), ">>>", "Sticker", ">>>", update.message.from_user.username)
            break
