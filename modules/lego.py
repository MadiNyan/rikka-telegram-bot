#!/usr/bin/python
# -*- coding: utf-8 -*-
from telegram.ext import CommandHandler, MessageHandler
from modules.custom_filters import caption_filter
from telegram.ext.dispatcher import run_async
from modules.send_image import send_image
from modules.get_image import get_image
from telegram import ChatAction
import subprocess
import datetime
import legofy
import yaml


def handler(dp):
    dp.add_handler(MessageHandler(caption_filter("/lego"), lego))
    dp.add_handler(CommandHandler("lego", lego))

# import paths
with open('config.yml', 'r') as f:
    path = yaml.load(f)["path"]["lego"]

extensions = (".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp")
name = "legofied"

@run_async
def lego(bot, update):
    if update.message.reply_to_message is not None:
        parts = update.message.text.split(" ", 1)
    else:
        parts = update.message.caption.split(" ", 1)
    if len(parts) == 1:
        size = 60
    else:
        try:
            size = int(parts[1])
        except:
            update.message.reply_text("Paremeter needs to be a number!")
            return
        if size > 100 or size < 1:
            update.message.reply_text("Baka, make it from 1 to 100!")
            return
    try:
        extension = get_image(bot, update, path)
    except:
        update.message.reply_text("Can't get the image! :(")
        return
    if extension not in extensions:
        update.message.reply_text("Unsupported file, onii-chan!")
        return False
    update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
    if extension == ".webp" or ".png":
        stick = "convert " + path + "original" + extension + " -background white -flatten " + path + "original" + extension
        subprocess.run(stick, shell=True)
    legofy.main(image_path=path + "original" + extension,
                output_path=path + name + extension,
                size=size, palette_mode=None, dither=False)
    send_image(bot, update, path, name, extension)
    print(datetime.datetime.now(), ">>>", "Done legofying", ">>>", update.message.from_user.username)