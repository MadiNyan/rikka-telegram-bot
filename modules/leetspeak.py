#!/usr/bin/python
# -*- coding: utf-8 -*-
from modules.logging import logging_decorator
from telegram.ext import PrefixHandler
from datetime import datetime
from functools import reduce


def module_init(gd):
    global leet_dictionary, extensions
    leet_dictionary = gd.config["leet_dictionary"]
    commands = gd.config["commands"]
    for command in commands:
        gd.dp.add_handler(PrefixHandler("/", command, leet))


@logging_decorator("leet")
def leet(update, context):
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
