from telegram import Update
from telegram.ext import PrefixHandler
from zalgo_text import zalgo

from modules.logging import logging_decorator


def module_init(gd):
    commands = gd.config["commands"]
    for command in commands:
        gd.application.add_handler(PrefixHandler("/", command, zalgo_txt))


@logging_decorator("zalgo")
async def zalgo_txt(update: Update, context):
    if update.message is None: return
    args = " ".join(context.args)
    if update.message.reply_to_message is not None:
        args = update.message.reply_to_message.text
        if len(update.message.reply_to_message.photo) > 0:
            args = update.message.reply_to_message.caption            
    if args == None:
        await update.message.reply_text("Type in some text!")
        return
    input_text = args
    if input_text == "":
        await update.message.reply_text("Type in some text!")
        return
    zalgofied_text = zalgo.zalgo().zalgofy(input_text)
    await update.message.reply_text(zalgofied_text)
