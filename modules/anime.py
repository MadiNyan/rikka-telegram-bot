# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from pybooru import Pybooru
from random import randint
import requests, yaml, datetime

with open('config.yml', 'r') as f:
    anime_folder = yaml.load(f)["path"]["anime"]

def get_anime(bot, update, query):
    client = Pybooru('yandere')
    tags = client.tags_list(query)
    try:
        tag_dict = next((item for item in tags if item["name"] == query))
        tag_count = tag_dict['count']
        if tag_count >= 100:
            posts_to_load = 100
        else:
            posts_to_load = tag_count
    except:
        posts_to_load = 100
    posts = client.posts_list(query, posts_to_load)
    random = randint(0, posts_to_load-1)
    image_post = "https://yande.re/post/show/"+str(posts[random]["id"])
    image_url = posts[random]["sample_url"]
    dl = requests.get(image_url)
    with open(anime_folder+"anime_temp.jpg", "wb") as f:
        f.write(dl.content)
    return image_post

def anime(bot, update, args):
    if args == []:
        input_query = ""
    else:
        input_query = ' '.join(args).lower()
    try:
        cap = get_anime(bot, update, input_query)
        with open(anime_folder+"anime_temp.jpg","rb") as f:
            bot.sendPhoto(update.message.chat_id, f, caption=cap, reply_to_message_id=update.message.message_id)
        print(datetime.datetime.now(), ">>>", "Sent anime:", input_query, ">>>", update.message.from_user.username)
    except:
        cap = get_anime(bot, update, "rating:s")
        with open(anime_folder+"anime_temp.jpg","rb") as f:
            bot.sendPhoto(update.message.chat_id, f, caption="Wrong tag, onii-chan, but here's one random pic:\n"+cap, reply_to_message_id=update.message.message_id)
        print(datetime.datetime.now(), ">>>", "Sent anime:", input_query, ">>>", update.message.from_user.username)