#!/usr/bin/python
# -*- coding: utf-8 -*-
from telegram.ext.dispatcher import run_async
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from telegram.ext import CommandHandler
from telegram import ChatAction
from random import randint
import datetime
import requests
import logging
import yaml

logging.getLogger('googleapiclient.discovery').setLevel(logging.ERROR)

def handler(dp):
    dp.add_handler(CommandHandler("img", g_search, pass_args=True))

with open("config.yml", "r") as f:
    yaml_file = yaml.load(f)
    dev_key = yaml_file["keys"]["google_dev_key"]
    cse_id = yaml_file["keys"]["google_cse_id"]


@run_async
def g_search(bot, update, args):
    if len(args) == 0:
        update.message.reply_text("You need a query to search!")
        return
    update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
    query = " ".join(args)
    try:
        final_img = get_image(query)
    except HttpError:
        update.message.reply_text("Sorry, my daily limit for search exceeded. Check back tomorrow!")
        return
    msg_text = "[link](%s)" % final_img
    update.message.reply_text(msg_text, parse_mode="Markdown")
    print (datetime.datetime.now(), ">>>", "Done /img", query, ">>>", update.message.from_user.username)


def get_image(query):
    service = build("customsearch", "v1", developerKey=dev_key, cache_discovery=False)
    result = service.cse().list(q=query, cx=cse_id, searchType="image").execute()
    random_item = randint(0, len(result["items"]))
    final_img = result["items"][random_item]["link"]
    return final_img
