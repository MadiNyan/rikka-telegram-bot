#!/usr/bin/python
# -*- coding: utf-8 -*-
from modules.logging import logging_decorator
from telegram.ext.dispatcher import run_async
from telegram.ext import PrefixHandler
from urllib.parse import quote_plus
from collections import Iterable
from telegram import ChatAction
from random import randint
import requests
import json
import re


def module_init(gd):
    commands_image = gd.config["commands_image"]
    commands_gif = gd.config["commands_gif"]
    for command in commands_image:
        gd.dp.add_handler(PrefixHandler("/", command, image_search))
    for command in commands_gif:
        gd.dp.add_handler(PrefixHandler("/", command, gif_search))


@run_async
@logging_decorator("img")
def image_search(update, context):
    query = google_search(update, context)
    return query


@run_async
@logging_decorator("gif")
def gif_search(update, context):
    query = google_search(update, context, gif=True)
    return query
    

def google_search(update, context, gif=False):
    query = quote_plus(" ".join(context.args))
    if len(query) == 0:
        update.message.reply_text("You need a query to search!")
        return
    update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
    try:
        final_img = single_result(get_image(query, gif))
    except:
        update.message.reply_text("Sorry, something gone wrong!")
        return
    if final_img is None:
        update.message.reply_text("Nothing found!")
        return
    msg_text = "[link](%s)" % final_img
    update.message.reply_text(msg_text, parse_mode="Markdown", disable_web_page_preview=False)


def get_image(query, gif=False):
    if gif:
        link = "https://www.google.ru/search?q={}&tbm=isch&tbs=itp%3Aanimated".format(query)
    else:
        link = "https://www.google.ru/search?q={}&tbm=isch".format(query)
    req = requests.get(link, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.142 Safari/537.36"})
    html_output = req.text
    googleregex = r"AF_initDataCallback\({key: 'ds:1', hash: '.', data:(.*), sideChannel: {}}\);<\/script><script"
    html_links = re.search(googleregex, html_output, re.M | re.I | re.S).group(1)
    full_json = json.loads(html_links)
    for a in full_json:
        if isinstance(a, Iterable):
            for b in a:
                if isinstance(b, Iterable):
                    for c in b:
                        if isinstance(c, Iterable):
                            for d in c:
                                if d == "GRID_STATE0":
                                    links_json = c[2]
                                    break
    imgs_list = []
    for i in links_json:
        try:
            imgs_list.append(i[1][3][0])
        except TypeError:
            pass
    return imgs_list


def single_result(links_list):
    if len(links_list) < 1:
        return None
    else:
        return links_list[randint(0, len(links_list)-1)]
