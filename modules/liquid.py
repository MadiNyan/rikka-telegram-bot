#!/usr/bin/python
# -*- coding: utf-8 -*-
from modules.get_image import get_image
import subprocess
import datetime
import yaml

# import path
with open("config.yml", "r") as f:
    path = yaml.load(f)["path"]["liquid"]


# get image, then rescale
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
        get_image(bot, update, path)
    except:
        update.message.reply_text("I can't get the image! :(")
        return
    identify = subprocess.Popen("identify " + path + "original.jpg", stdout=subprocess.PIPE).communicate()[0]
    res = str(identify.split()[2])[2:-1]
    size = str(100 - (power / 1.3))
    x = "convert " + path + "original.jpg -liquid-rescale " + size + "%x" + size + "% -resize " + res + "! " + path + "liquid.jpg"
    subprocess.run(x, shell=True)
    with open(path + "liquid.jpg", "rb") as f:
        update.message.reply_photo(f)
    print(datetime.datetime.now(), ">>>", "Done liquid rescale", ">>>", update.message.from_user.username)
