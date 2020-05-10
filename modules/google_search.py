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
    commands_image = gd.config["commands_image"]
    commands_gif = gd.config["commands_gif"]
    for command in commands_image:
        gd.dp.add_handler(CommandHandler(command, image_search, pass_args=True))
    for command in commands_gif:
        gd.dp.add_handler(CommandHandler(command, gif_search, pass_args=True))


@run_async
@logging_decorator("img")
def image_search(bot, update, args):
    query = " ".join(args)
    google_args = {"keywords":query, "limit":30, "no_download":True}
    query = search(bot, update, args, google_args)
    return query


@run_async
@logging_decorator("gif")
def gif_search(bot, update, args):
    query = " ".join(args)
    google_args = {"keywords":query, "limit":30, "no_download":True, "format":"gif"}
    query = search(bot, update, args, google_args)
    return query
    

def search(bot, update, args, google_args):
    if len(args) == 0:
        update.message.reply_text("You need a query to search!")
        return
    update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
    query = " ".join(args)
    try:
        final_img = get_image(query, google_args)
    except:
        update.message.reply_text("Sorry, something gone wrong!")
        return
    if final_img is None:
        update.message.reply_text("Nothing found!")
        return
    msg_text = "[link](%s)" % final_img
    update.message.reply_text(msg_text, parse_mode="Markdown", disable_web_page_preview=False)
    return query


def get_image(query, google_args):
    sys.stdout = io.StringIO()
    response = google_images_download.googleimagesdownload()
    
    response.download(google_args)
    result = sys.stdout.getvalue()
    sys.stdout.close()
    sys.stdout = sys.__stdout__
    urls = re.findall(r'(https?://\S+)', result)
    image_to_send = urls[randint(0, 29)]
    return image_to_send
