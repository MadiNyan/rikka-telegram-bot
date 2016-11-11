#!/usr/bin/python
# -*- coding: utf-8 -*-
from telegram.ext import CommandHandler, MessageHandler
from modules.custom_filters import caption_filter
from telegram.ext.dispatcher import run_async
from modules.memegenerator import make_meme
from modules.send_image import send_image
from modules.get_image import get_image
from telegram import ChatAction
import datetime
import yaml


def handler(dp):
    dp.add_handler(MessageHandler(caption_filter("/meme"), meme))
    dp.add_handler(CommandHandler("meme", meme))

# import paths
with open("config.yml", "r") as f:
    path = yaml.load(f)["path"]["memes"]

extensions = (".jpg", ".jpeg", ".png", ".webp")
name = "meme"


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
        make_meme(split_text[0], split_text[1], path + "original" + extension, extension)
    else:
        make_meme("", split_text[0], path + "original" + extension, extension)
    send_image(bot, update, path, name, extension)
    print (datetime.datetime.now(), ">>>", "Done meme", ">>>",
           update.message.from_user.username)
