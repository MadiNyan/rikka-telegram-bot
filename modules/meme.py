#!/usr/bin/python
# -*- coding: utf-8 -*-
from modules.get_image import get_image
from modules.memegenerator import make_meme
from telegram import ChatAction
import datetime
import yaml

# import paths
with open("config.yml", "r") as f:
    meme_folder = yaml.load(f)["path"]["memes"]


def meme(bot, update):
    meme_splitter = "@"
    if update.message.reply_to_message is not None:
        initial_text = "".join(update.message.text[6:]).upper()
    else:
        initial_text = "".join(update.message.caption[6:]).upper()
    split_text = initial_text.split(meme_splitter)
    try:
        get_image(bot, update, meme_folder)
    except:
        update.message.reply_text("Can't get the image! :(")
        return
    update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
    if split_text[0] == "":
        update.message.reply_text("Type in some text!")
        return
    elif len(split_text) > 1:
        make_meme(split_text[0], split_text[1], meme_folder+"original.jpg")
    else:
        make_meme("", split_text[0], meme_folder+"original.jpg")
    with open(meme_folder+"meme.jpg", "rb") as f:
        update.message.reply_photo(f)
    print (datetime.datetime.now(), ">>>", "Done meme", ">>>",
           update.message.from_user.username)
