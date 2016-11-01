#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from pybooru import Pybooru
from random import randint
from telegram import ChatAction
import requests
import yaml
import datetime

with open("config.yml", "r") as f:
    anime_folder = yaml.load(f)["path"]["anime"]


def get_anime(update, query):
    update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
    client = Pybooru("yandere")
    max_posts_to_load = 200
    posts = client.posts_list(query, max_posts_to_load)
    post_count = len(posts)
    random = randint(0, post_count - 1)
    image_post = "https://yande.re/post/show/" + str(posts[random]["id"])
    image_url = posts[random]["sample_url"]
    dl = requests.get(image_url)
    with open(anime_folder + "anime_temp.jpg", "wb") as f:
        f.write(dl.content)
    return image_post


def anime(bot, update, args):
    if args == []:
        input_query = "rating:s"
    else:
        input_query = " ".join(args).lower()
    try:
        cap = get_anime(update, input_query)
        with open(anime_folder + "anime_temp.jpg", "rb") as f:
            update.message.reply_photo(f, caption=cap)
        print (datetime.datetime.now(),
               ">>> Sent anime:", input_query, ">>>",
               update.message.from_user.username)
    except:
        cap = get_anime(update, "rating:s")
        with open(anime_folder + "anime_temp.jpg", "rb") as f:
            update.message.reply_photo(f, caption="Nothing found, onii-chan, but here's one random pic:\n" + cap)
        print (datetime.datetime.now(),
               ">>> Tag not found:", input_query, ", sent random", ">>>",
               update.message.from_user.username)
