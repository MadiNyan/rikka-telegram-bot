#!/usr/bin/python
# -*- coding: utf-8 -*-
from modules.logging import log_command
from telegram.ext import CommandHandler
from datetime import datetime
from functools import reduce


def module_init(gd):
    global leet_dictionary, extensions
    leet_dictionary = gd.config["leet_dictionary"]
    commands = gd.config["commands"]
    for command in commands:
        gd.dp.add_handler(CommandHandler(command, leet, pass_args=True))


def leet(bot, update, args):
    current_time = datetime.strftime(datetime.now(), "%d.%m.%Y %H:%M:%S")
    if update.message.reply_to_message is not None:
        args = update.message.reply_to_message.text
        args = args.split(" ")
    text_leet = " ".join(args).lower()
    if text_leet == "":
        return
    replace_dict = []
    with open(leet_dictionary, "r", encoding="UTF-8") as file:
        for i in file.readlines():
            tmp = i.split(",")
            try:
                replace_dict.append((tmp[0], tmp[1]))
            except:
                pass
    text_leet = reduce(lambda a, kv: a.replace(*kv), replace_dict, text_leet)
    update.message.reply_text(text_leet)
    print(current_time, ">", "/leetspeak", ">", update.message.from_user.username)
    log_command(bot, update, current_time, "leetspeak")
