#!/usr/bin/python
# -*- coding: utf-8 -*-
from telegram.ext import MessageHandler, Filters
from datetime import datetime


def module_init(gd):
    global keywords, sticker_path
    keywords = gd.config["keywords"]
    sticker_path = gd.config["sticker_path"]
    gd.dp.add_handler(MessageHandler(Filters.text, sticker_rep))


def sticker_rep(bot, update):
    current_time = datetime.strftime(datetime.now(), "%d.%m.%Y %H:%M:%S")
    if update.effective_message.chat.type == "channel":
        return
    for word in keywords:
        if word in update.message.text:
            with open(sticker_path, "rb") as sticker:
                update.message.reply_sticker(sticker)
            print(current_time, ">", "sticker", ">", update.message.from_user.username)
            break
