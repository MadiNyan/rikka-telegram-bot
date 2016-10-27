#!/usr/bin/python
# -*- coding: utf-8 -*-
from py_bing_search import PyBingImageSearch, PyBingVideoSearch, \
    PyBingNewsSearch
from random import randint
import datetime
import yaml

with open("config.yml", "r") as f:
    key = yaml.load(f)["keys"]["bing_api_key"]


def img_search(bot, update, args):
    if len(args) == 0:
        update.message.reply_text("You need a query to search!")
        return
    search = " ".join(args)
    bing_image = PyBingImageSearch(key, search,
                                   custom_params="&Adult='Off'")
    result = bing_image.search(limit=40, format="json")
    if len(result) == 0:
        update.message.reply_text("Sorry, I can't find anything :(")
    else:
        img = randint(0, len(result) - 1)
        link = result[img].media_url
        text = "[link](%s)" % link
        update.message.reply_text(text, parse_mode="Markdown")
        print (datetime.datetime.now(), ">>>", "Done /img", ">>>",
               update.message.from_user.username)


def vid_search(bot, update, args):
    if len(args) == 0:
        update.message.reply_text("You need a query to search!")
        return
    search = " ".join(args)
    bing_video = PyBingVideoSearch(key, search,
                                   custom_params="&Adult='Off'")
    result = bing_video.search(limit=30, format="json")
    if len(result) == 0:
        update.message.reply_text("Sorry, I can't find anything :(")
    else:
        vid_list = []
        for i in range(0, len(result) - 1):
            if "youtube" in result[i].media_url:
                vid_list.append(result[i].media_url)
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


def news_search(bot, update, args):
    search = " ".join(args)
    bing_news = PyBingNewsSearch(key, search)
    result = bing_news.search(limit=20, format="json")
    if len(result) == 0:
        update.message.reply_text("Sorry, I can't find anything :(")
    else:
        news = randint(0, len(result) - 1)
        link = result[news].url
        bot.sendMessage(chat_id=update.message.chat_id, text=link,
                        reply_to_message_id=update.message.message_id,
                        parse_mode="Markdown")
        print (datetime.datetime.now(), ">>>", "Done /news", ">>>",
               update.message.from_user.username)
