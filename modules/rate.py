#!/usr/bin/python
# -*- coding: utf-8 -*-
from telegram.ext import CommandHandler
from modules.logging import log_command
from random import random, seed
from datetime import datetime


def module_init(gd):
    commands = gd.config["commands"]
    for command in commands:
        gd.dp.add_handler(CommandHandler(command, rate, pass_args=True))


def ifint(number):
    if number.is_integer():
        number = int(number)
        return number
    else:
        return number


def rate(bot, update, args):
    current_time = datetime.strftime(datetime.now(), "%d.%m.%Y %H:%M:%S")
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
    print(current_time, ">", "/rate", ">", update.message.from_user.username)
    log_command(bot, update, current_time, "rate")
