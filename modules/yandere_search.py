#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from telegram.ext.dispatcher import run_async
from telegram.ext import CommandHandler
from modules.logging import log_command
from telegram import ChatAction
from datetime import datetime
from pybooru import Moebooru
from random import randint
import requests


def module_init(gd):
    global path
    path = gd.config["path"]
    commands = gd.config["commands"]
    for command in commands:
        gd.dp.add_handler(CommandHandler(command, yandere_search, pass_args=True))


def get_anime(update, query, filename):
    update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
    client = Moebooru("yandere")
    max_posts_to_load = 200
    posts = client.post_list(tags=query, limit=max_posts_to_load)
    post_count = len(posts)
    random = randint(0, post_count - 1)
    image_post = "https://yande.re/post/show/" + str(posts[random]["id"])
    image_url = posts[random]["sample_url"]
    dl = requests.get(image_url)
    with open(path + filename + ".jpg", "wb") as f:
        f.write(dl.content)
    return image_post


@run_async
def yandere_search(bot, update, args):
    current_time = datetime.strftime(datetime.now(), "%d.%m.%Y %H:%M:%S")
    filename = datetime.now().strftime("%d%m%y-%H%M%S%f")
    if args == []:
        input_query = "rating:s"
    else:
        input_query = " ".join(args).lower()
    try:
        cap = get_anime(update, input_query, filename)
        with open(path + filename + ".jpg", "rb") as f:
            update.message.reply_photo(f, caption=cap)
        print (current_time, "> /yandere", input_query, ">", update.message.from_user.username)
    except:
        cap = get_anime(update, "rating:s", filename)
        with open(path + filename + ".jpg", "rb") as f:
            update.message.reply_photo(f, caption="Nothing found, here's one random pic:\n" + cap)
        print (current_time,"> /yandere not found:", input_query, ", sent random", ">", update.message.from_user.username)
    log_command(bot, update, current_time, "yandere")
