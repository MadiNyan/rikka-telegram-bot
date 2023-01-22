#!/usr/bin/python
# -*- coding: utf-8 -*-
from modules.logging import logging_decorator
from telegram.ext.dispatcher import run_async
from telegram.ext import PrefixHandler
from telegram import ChatAction
import requests
import random
import urllib.parse

yandere_request_link = "https://yande.re/post.json?limit=100"
yandere_post_link = "https://yande.re/post/show/"
gelbooru_request_link = "https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1"
gelbooru_post_link = "https://gelbooru.com/index.php?page=post&s=view&id="


def module_init(gd):
    global proxies
    commands_gelbooru = gd.config["commands_gelbooru"]
    commands_yandere = gd.config["commands_yandere"]
    proxyuser = gd.config["proxy"]["user"]
    proxypassword = gd.config["proxy"]["password"]
    proxyserver = gd.config["proxy"]["server"]
    proxylink = "socks5://"+proxyuser+":"+proxypassword+"@"+proxyserver
    proxies = {"https" : proxylink}
    for command in commands_gelbooru:
        gd.dp.add_handler(PrefixHandler("/", command, gelbooru_search))
    for command in commands_yandere:
        gd.dp.add_handler(PrefixHandler("/", command, yandere_search))


@run_async
@logging_decorator("yandere")
def yandere_search(update, context):
    query = search(update, context, yandere_request_link, yandere_post_link)
    return query


@run_async
@logging_decorator("gelbooru")
def gelbooru_search(update, context):
    query = search(update, context, gelbooru_request_link, gelbooru_post_link, 'gelbooru')
    return query


def search(update, context, request_link, image_link, search_place='yandere'):
    update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
    query = " ".join(context.args)
    try:
        if search_place == 'gelbooru':
            direct_link, page_link, sample_link = get_gelbooru_image(query, request_link, image_link)
        else:
            direct_link, page_link, sample_link = get_image(query, request_link, image_link)
            
    except:
        update.message.reply_text("Sorry, something went wrong!")
        return
    if direct_link is None:
        update.message.reply_text("Nothing found!")
        return
    msg_text = "[Image]({})".format(direct_link) + "\n" + "[View post]({})".format(page_link)
    update.message.reply_text(msg_text, parse_mode="Markdown")
    return query


def get_gelbooru_image(query, request_link, image_link):
    params = {"tags": query.replace(' ', '+')}  # replace space for plus symbol
    params_str = urllib.parse.urlencode(params, safe=':+')  # prevent percenting symbols in request
    response = requests.get(request_link, params=params, proxies=proxies)
    result_obj = response.json()
    if not response.text:
        return None, None
    if not result_obj:
        return None, None
    if result_obj['@attributes']['count'] == 0:  # check if nothing found
        return None, None
    post = random.choice(result_obj['post'])  # get random post from list
    direct_link, page_link, sample_link = post.get("file_url"), image_link+str(post.get("id")), post.get("sample_url")
    return direct_link, page_link, sample_link


def get_image(query, request_link, image_link):
    params = {"tags": query}
    response = requests.get(request_link, params=params, proxies=proxies)
    result_list = response.json()
    if not response.text:
        return None, None
    if not result_list:
        return None, None
    post = random.choice(result_list)
    direct_link, page_link, sample_link = post.get("file_url"), image_link+str(post.get("id")), post.get("sample_url")
    return direct_link, page_link, sample_link
