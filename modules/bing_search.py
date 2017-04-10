#!/usr/bin/python
# -*- coding: utf-8 -*-
from py_ms_cognitive import PyMsCognitiveImageSearch, PyMsCognitiveVideoSearch, PyMsCognitiveNewsSearch
from telegram.ext import CommandHandler
from telegram.ext.dispatcher import run_async
from telegram import ChatAction
from random import randint
import datetime
import requests
import yaml


def handler(dp):
    dp.add_handler(CommandHandler("img", img_search, pass_args=True))
    dp.add_handler(CommandHandler("vid", vid_search, pass_args=True))
    dp.add_handler(CommandHandler("news", news_search, pass_args=True))

with open("config.yml", "r") as f:
    key = yaml.load(f)["keys"]["bing_api_key"]


@run_async
def img_search(bot, update, args):
    if len(args) == 0:
        update.message.reply_text("You need a query to search!")
        return
    update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
    search = " ".join(args)
    bing_image = PyMsCognitiveImageSearch(key, search,
                                   custom_params={"adlt": "off"})
    result = bing_image.search(limit=40, format="json")
    if len(result) == 0:
        update.message.reply_text("Sorry, I can't find anything :(")
    else:
        img = randint(0, len(result) - 1)
        r = requests.get(result[img].content_url)
        link = r.url
        text = "[link](%s)" % link
        update.message.reply_text(text, parse_mode="Markdown")
        print (datetime.datetime.now(), ">>>", "Done /img", ">>>",
               update.message.from_user.username)


@run_async
def vid_search(bot, update, args):
    if len(args) == 0:
        update.message.reply_text("You need a query to search!")
        return
    update.message.chat.send_action(ChatAction.UPLOAD_VIDEO)
    search = " ".join(args)
    bing_video = PyMsCognitiveVideoSearch(key, search,
                                   custom_params={"adlt": "off"})
    result = bing_video.search(limit=20, format="json")
    if len(result) == 0:
        update.message.reply_text("Sorry, I can't find anything :(")
    else:
        vid_list = []
        for i in range(0, len(result) - 1):
            if "youtube" in result[i].host_page_display_url:
                vid_list.append(result[i].host_page_display_url)
        if len(vid_list) == 0:
            update.message.reply_text("Sorry, I can't find anything :(")
        else:
            vid = randint(0, len(vid_list) - 1)
            link = vid_list[vid]
            text = "[link](%s)" % link
            bot.sendMessage(chat_id=update.message.chat_id, text=text,
                            reply_to_message_id=update.message.message_id,
                            parse_mode="Markdown")
            print (datetime.datetime.now(), ">>>", "Done /vid", ">>>",
                   update.message.from_user.username)


@run_async
def news_search(bot, update, args):
    update.message.chat.send_action(ChatAction.TYPING)
    search = " ".join(args)
    bing_news = PyMsCognitiveNewsSearch(key, search)
    result = bing_news.search(limit=20, format="json")
    if len(result) == 0:
        update.message.reply_text("Sorry, I can't find anything :(")
    else:
        news = randint(0, len(result) - 1)
        r = requests.get(result[news].url)
        link = r.url
        bot.sendMessage(chat_id=update.message.chat_id, text=link,
                        reply_to_message_id=update.message.message_id,
                        parse_mode="Markdown")
        print (datetime.datetime.now(), ">>>", "Done /news", ">>>",
               update.message.from_user.username)
