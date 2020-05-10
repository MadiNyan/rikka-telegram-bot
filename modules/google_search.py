#!/usr/bin/python
# -*- coding: utf-8 -*-
from modules.logging import logging_decorator
from google_images_download import google_images_download
from telegram.ext.dispatcher import run_async
from telegram.ext import CommandHandler
from telegram import ChatAction
from random import randint
import logging
import sys
import re
import io


def module_init(gd):
    commands = gd.config["commands"]
    for command in commands:
        gd.dp.add_handler(CommandHandler(command, g_search, pass_args=True))


@run_async
@logging_decorator("img")
def g_search(bot, update, args):
    if len(args) == 0:
        update.message.reply_text("You need a query to search!")
        return
    update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
    query = " ".join(args)
    try:
        final_img = get_image(query)
    except:
        update.message.reply_text("Sorry, something gone wrong!")
        return
    if final_img is None:
        update.message.reply_text("Nothing found!")
        return
    msg_text = "[link](%s)" % final_img
    update.message.reply_text(msg_text, parse_mode="Markdown")
    return query


def get_image(query):
    sys.stdout = io.StringIO()
    response = google_images_download.googleimagesdownload()
    arguments = {"keywords":query, "limit":30, "print_urls":True, "no_download":True}
    response.download(arguments)
    result = sys.stdout.getvalue()
    sys.stdout.close()
    sys.stdout = sys.__stdout__
    urls = re.findall(r'(https?://\S+)', result)
    image_to_send = urls[randint(0, 29)]
    return image_to_send