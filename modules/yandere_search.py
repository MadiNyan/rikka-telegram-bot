#!/usr/bin/python
# -*- coding: utf-8 -*-
from modules.logging import logging_decorator
from telegram.ext import CommandHandler
from telegram import ChatAction
import requests
import random


def module_init(gd):
    commands = gd.config["commands"]
    for command in commands:
        gd.dp.add_handler(CommandHandler(command, yandere_search, pass_args=True))


@logging_decorator("yandere")
def yandere_search(bot, update, args):
    update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
    query = " ".join(args)
    try:
        direct_link, page_link = get_image(query)
    except:
        update.message.reply_text("Sorry, something went wrong!")
        return
    if direct_link is None:
        update.message.reply_text("Nothing found!")
        return
    msg_text = "[Image]({})".format(direct_link) + "\n" + "[View post]({})".format(page_link)
    update.message.reply_text(msg_text, parse_mode="Markdown")
    return query

    
def get_image(query):
    params = {"tags": query}
    response = requests.get("https://yande.re/post.json?", params=params)
    result_list = response.json()
    if not response.text:
        return None, None
    if not result_list:
        return None, None
    post = random.choice(result_list)
    direct_link, page_link = post.get("file_url"), "https://yande.re/post/show/"+str(post.get("id"))
    return direct_link, page_link