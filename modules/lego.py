#!/usr/bin/python
# -*- coding: utf-8 -*-
from modules.utils import caption_filter, get_image, send_image, get_param
from telegram.ext import CommandHandler, MessageHandler
from telegram.ext.dispatcher import run_async
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
    size = get_param(update)
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
    send_image(update, path, name, extension)
    print(datetime.datetime.now(), ">>>", "Done legofying", ">>>", update.message.from_user.username)
