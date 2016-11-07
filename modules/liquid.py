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
import yaml


def handler(dp):
    dp.add_handler(MessageHandler(caption_filter("/liq"), liquid))
    dp.add_handler(CommandHandler("liq", liquid))

# import path
with open("config.yml", "r") as f:
    path = yaml.load(f)["path"]["liquid"]


# get image, then rescale
@run_async
def liquid(bot, update):
    if update.message.reply_to_message is not None:
        parts = update.message.text.split(" ", 1)
    else:
        parts = update.message.caption.split(" ", 1)
    if len(parts) == 1:
        power = 50
    else:
        try:
            power = int(parts[1])
        except:
            update.message.reply_text("Paremeter needs to be a number!")
            return
        if power > 100 or power < 1:
            update.message.reply_text("Baka, make it from 1 to 100!")
            return
    try:
        extension = get_image(bot, update, path)
    except:
        update.message.reply_text("I can't get the image! :(")
        return
    update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
    identify = subprocess.Popen("identify " + path + "original" + extension, stdout=subprocess.PIPE).communicate()[0]
    res = str(identify.split()[2])[2:-1]
    size = str(100 - (power / 1.3))
    name = "liquid"
    x = "convert " + path + "original" + extension + " -liquid-rescale " + \
         size + "%x" + size + "% -resize " + res + "! " + path + name + extension
    subprocess.run(x, shell=True)
    if extension == ".mp4":
        mp4fix = "ffmpeg -loglevel panic -i " + path + name + extension + \
                  " -an -vf scale=trunc(iw/2)*2:trunc(ih/2)*2 \
                  -pix_fmt yuv420p -c:v libx264 -profile:v high -level:v 2.0 " \
                  + path + name + "_mp4" + extension + " -y"
        subprocess.run(mp4fix, shell=True)
        name = name + "_mp4"
    send_image(bot, update, path, name, extension)
    print(datetime.datetime.now(), ">>>", "Done liquid rescale", ">>>", update.message.from_user.username)
