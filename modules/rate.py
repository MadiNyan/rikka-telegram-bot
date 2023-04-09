from random import random, seed

from telegram import Update
from telegram.ext import PrefixHandler

from modules.logging import logging_decorator


def module_init(gd):
    commands = gd.config["commands"]
    for command in commands:
        gd.application.add_handler(PrefixHandler("/", command, rate))


def ifint(number):
    if number.is_integer():
        number = int(number)
        return number
    else:
        return number


@logging_decorator("rate")
async def rate(update: Update, context):
    if update.message is None: return
    if update.message.reply_to_message is not None and update.message.reply_to_message.text is not None:
        args = update.message.reply_to_message.text.split(" ")
    else:
        args = context.args
    string = " ".join(args).lower()
    if string == "":
        seed()
    else:
        seed(string)
    rng = random() * 10
    rounded = round(rng * 2) / 2
    rating = str(ifint(rounded))
    await update.message.reply_text("🤔 I rate this "+rating+"/10")
