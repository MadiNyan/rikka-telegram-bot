#!/usr/bin/python
# -*- coding: utf-8 -*-
from modules.logging import logging_decorator
from telegram.ext import PrefixHandler
from datetime import datetime
from zalgo_text import zalgo    


def module_init(gd):
    commands = gd.config["commands"]
    for command in commands:
        gd.dp.add_handler(PrefixHandler("/", command, zalgo_txt))


@logging_decorator("zalgo")
def zalgo_txt(update, context):
    if update.message.reply_to_message is not None:
        args = update.message.reply_to_message.text
        args = args.split(" ")
    input_text = " ".join(context.args).lower()
    if input_text == "":
        update.message.reply_text("Type in some text!")
        return
    zalgofied_text = zalgo.zalgo().zalgofy(input_text)
    update.message.reply_text(zalgofied_text)
