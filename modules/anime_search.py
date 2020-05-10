#!/usr/bin/python
# -*- coding: utf-8 -*-
from modules.logging import logging_decorator
from telegram.ext import CommandHandler
from telegram import ChatAction
import requests
import random


def module_init(gd):      
    commands_gelbooru = gd.config["commands_gelbooru"]
    commands_yandere = gd.config["commands_yandere"]
    for command in commands_gelbooru:
        gd.dp.add_handler(CommandHandler(command, gelbooru_search, pass_args=True))
    for command in commands_yandere:
        gd.dp.add_handler(CommandHandler(command, yandere_search, pass_args=True))


@logging_decorator("yandere")
def yandere_search(bot, update, args):
    request_link = "https://yande.re/post.json?"
    image_link = "https://yande.re/post/show/"
    search(bot, update, args, request_link, image_link)


@logging_decorator("gelbooru")
def gelbooru_search(bot, update, args):
    request_link = "https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1"
    image_link = "https://gelbooru.com/index.php?page=post&s=view&id="
    search(bot, update, args, request_link, image_link)


def search(bot, update, args, request_link, image_link):
    update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
    query = " ".join(args)
    try:
        direct_link, page_link = get_image(query, request_link, image_link)
    except:
        update.message.reply_text("Sorry, something went wrong!")
        return
    if direct_link is None:
        update.message.reply_text("Nothing found!")
        return
    msg_text = "[Image]({})".format(direct_link) + "\n" + "[View post]({})".format(page_link)
    update.message.reply_text(msg_text, parse_mode="Markdown")


def get_image(query, request_link, image_link):
    params = {"tags": query}
    response = requests.get(request_link, params=params)
    result_list = response.json()
    if not response.text:
        return None, None
    if not result_list:
        return None, None
    post = random.choice(result_list)
    direct_link, page_link = post.get("file_url"), image_link+str(post.get("id"))
    return direct_link, page_link
