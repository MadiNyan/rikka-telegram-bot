#!/usr/bin/python
# -*- coding: utf-8 -*-
from modules.logging import log_command
from telegram.ext import CommandHandler
from datetime import datetime
from zalgo_text import zalgo    


def module_init(gd):
    commands = gd.config["commands"]
    for command in commands:
        gd.dp.add_handler(CommandHandler(command, zalgo_txt, pass_args=True))


def zalgo_txt(bot, update, args):
    current_time = datetime.strftime(datetime.now(), "%d.%m.%Y %H:%M:%S")
    if update.message.reply_to_message is not None:
        args = update.message.reply_to_message.text
        args = args.split(" ")
    input_text = " ".join(args).lower()
    if input_text == "":
        update.message.reply_text("Type in some text!")
        return
    zalgofied_text = zalgo.zalgo().zalgofy(input_text)
    update.message.reply_text(zalgofied_text)
    print(current_time, ">", "/zalgo", ">", update.message.from_user.username)
    log_command(bot, update, current_time, "zalgo")
