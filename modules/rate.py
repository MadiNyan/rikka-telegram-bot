#!/usr/bin/python
# -*- coding: utf-8 -*-
from telegram.ext import CommandHandler
from random import random, seed
import datetime


def handler(dp):
    dp.add_handler(CommandHandler("rate", rate, pass_args=True))


def ifint(number):
    if number.is_integer():
        number = int(number)
        return number
    else:
        return number


def rate(bot, update, args):
    if update.message.reply_to_message is not None:
        if update.message.reply_to_message.text is not None:
            args = update.message.reply_to_message.text.split(" ")
    string = " ".join(args).lower()
    if string == "":
        seed()
    else:
        seed(string)
    rng = random() * 10
    rounded = round(rng * 2) / 2
    rating = str(ifint(rounded))
    update.message.reply_text("🤔 I rate this "+rating+"/10")
    print(datetime.datetime.now(), ">>>", "Done rate", ">>>", update.message.from_user.username)
