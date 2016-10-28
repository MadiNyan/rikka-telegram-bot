#!/usr/bin/python
# -*- coding: utf-8 -*-
from modules.get_image import get_image
import legofy
import datetime
import yaml

# import paths
with open('config.yml', 'r') as f:
    lego_folder = yaml.load(f)["path"]["lego"]


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
        if size > 100:
            update.message.reply_text("Baka, make it from 1 to 100!")
            return
    try:
        get_image(bot, update, lego_folder)
    except:
        update.message.reply_text("Can't get the image! :(")
        return
    legofy.main(image_path=lego_folder+"original.jpg",
                output_path=lego_folder+"legofied.jpg",
                size=size, palette_mode=None, dither=False)
    with open(lego_folder+"legofied.jpg", "rb") as f:
        update.message.reply_photo(f)
    print(datetime.datetime.now(), ">>>", "Done legofying", ">>>", update.message.from_user.username)