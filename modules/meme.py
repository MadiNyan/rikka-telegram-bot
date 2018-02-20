#!/usr/bin/python
# -*- coding: utf-8 -*-
from modules.utils import caption_filter, get_image, send_image
from telegram.ext import CommandHandler, MessageHandler
from telegram.ext.dispatcher import run_async
from modules.memegenerator import make_meme
from modules.logging import log_command
from telegram import ChatAction
from datetime import datetime


def module_init(gd):
    global path, extensions, fonts_dict
    path = gd.config["path"]
    extensions = gd.config["extensions"]
    commands = gd.config["commands"]
    fonts_dict = {}
    for i in gd.config["fonts"]:
        fonts_dict[gd.config["fonts"][i]["name"]] = gd.config["fonts"][i]["path"]
    for command in commands:
        gd.dp.add_handler(MessageHandler(caption_filter("/"+command), meme))
        gd.dp.add_handler(CommandHandler(commands, meme))


def text_format(split_text):
    if len(split_text) == 1 and split_text[0] == "":
        update.message.reply_text("Type in some text!")
        return
    elif len(split_text) > 1 and split_text[0] == "" and split_text[1] == "":
        update.message.reply_text("Type in some text!")
        return
    elif len(split_text) == 1:
        top_text = None
        bottom_text = split_text[0]
        bottom_text.rstrip()
    elif len(split_text) > 1 and split_text[0] == "":
        top_text = None
        bottom_text = split_text[1]
        bottom_text.lstrip()
    elif len(split_text) > 1 and split_text[1] == "":
        top_text = split_text[0]
        top_text.rstrip()
        bottom_text = None
    else:
        top_text = split_text[0].rstrip()
        top_text.rstrip()
        bottom_text = split_text[1]
        bottom_text.lstrip()
    return top_text, bottom_text


@run_async
def meme(bot, update):
    current_time = datetime.strftime(datetime.now(), "%d.%m.%Y %H:%M:%S")
    filename = datetime.now().strftime("%d%m%y-%H%M%S%f")

    if update.message.reply_to_message is not None:
        args = update.message.text.split(" ")
    else:
        args = update.message.caption.split(" ")
    args = args[1:]

    font = fonts_dict["impact"]
    for i in fonts_dict:
        if "-"+i in args[0] or "-"+i[0] in args[0]:
            font = fonts_dict[i]
            args = args[1:]
            break

    initial_text = " ".join(args)
    split_text = initial_text.split("@", maxsplit=1)

    update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
    try:
        extension = get_image(bot, update, path, filename)
    except:
        update.message.reply_text("Can't get the image! :(")
        return
    if extension not in extensions:
        update.message.reply_text("Unsupported file, onii-chan!")
        return

    top_text, bottom_text = text_format(split_text)
    make_meme(top_text, bottom_text, filename, extension, path, font)
    update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
    send_image(update, path, filename+"-meme", extension)
    print (current_time, ">", "/meme", ">", update.message.from_user.username)
    log_command(bot, update, current_time, "meme")
