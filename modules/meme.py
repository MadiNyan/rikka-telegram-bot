#!/usr/bin/python
# -*- coding: utf-8 -*-
from modules.utils import caption_filter, get_image, send_image
from telegram.ext import CommandHandler, MessageHandler
from telegram.ext.dispatcher import run_async
from modules.memegenerator import make_meme
from telegram import ChatAction
import datetime
import yaml


def module_init(gd):
    global path, extensions, name, meme_font
    path = gd.config["path"]
    extensions = gd.config["extensions"]
    commands = gd.config["commands"]
    meme_font = gd.config["fontpath"]
    name = "meme"
    for command in commands:
        gd.dp.add_handler(MessageHandler(caption_filter("/"+command), meme))
        gd.dp.add_handler(CommandHandler(command, meme))


@run_async
def meme(bot, update):
    meme_splitter = "@"
    if update.message.reply_to_message is not None:
        initial_text = "".join(update.message.text[6:]).upper()
    else:
        initial_text = "".join(update.message.caption[6:]).upper()
    split_text = initial_text.split(meme_splitter)
    try:
        extension = get_image(bot, update, path)
    except:
        update.message.reply_text("Can't get the image! :(")
        return
    if extension not in extensions:
        update.message.reply_text("Unsupported file, onii-chan!")
        return False
    update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
    if split_text[0] == "":
        update.message.reply_text("Type in some text!")
        return
    elif len(split_text) > 1:
        make_meme(split_text[0], split_text[1], path + "original" + extension, extension, path, meme_font)
    else:
        make_meme("  ", split_text[0], path + "original" + extension, extension, path, meme_font)
    send_image(update, path, name, extension)
    print (datetime.datetime.now(), ">>>", "Done meme", ">>>",
           update.message.from_user.username)
