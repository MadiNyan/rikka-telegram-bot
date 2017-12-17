#!/usr/bin/python
# -*- coding: utf-8 -*-
from telegram.ext.dispatcher import run_async
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from telegram.ext import CommandHandler
from modules.logging import log_command
from datetime import datetime
from telegram import ChatAction
from random import randint
import logging


def module_init(gd):
    global dev_key, cse_id
    dev_key = gd.config["google_dev_key"]
    cse_id = gd.config["google_cse_id"]
    commands = gd.config["commands_image"]
    for command in commands:
        gd.dp.add_handler(CommandHandler(command, g_search, pass_args=True))
    logging.getLogger('googleapiclient.discovery').setLevel(logging.ERROR)


@run_async
def g_search(bot, update, args):
    current_time = datetime.strftime(datetime.now(), "%d.%m.%Y %H:%M:%S")
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
    if final_img is None:
        update.message.reply_text("Nothing found!")
        return
    msg_text = "[link](%s)" % final_img
    update.message.reply_text(msg_text, parse_mode="Markdown")
    print (current_time, ">", "/img", query, ">", update.message.from_user.username)
    log_command(bot, update, current_time, "img")


def get_image(query):
    service = build("customsearch", "v1", developerKey=dev_key, cache_discovery=False)
    result = service.cse().list(q=query, cx=cse_id, searchType="image").execute()
    total_results = int(result["queries"]["request"][0]["totalResults"])
    if total_results < 1:
        return None
    random_item = randint(0, len(result["items"]))
    final_img = result["items"][random_item]["link"]
    return final_img
