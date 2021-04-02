#!/usr/bin/python
# -*- coding: utf-8 -*-
from modules.anime_search import get_image, proxies, yandere_request_link
from modules.logging import logging_decorator
from telegram.ext import PrefixHandler
from telegram.ext.dispatcher import run_async
from modules.memegenerator import make_meme
from modules.meme import fonts_dict, text_format
from modules.nya import files
from telegram import ChatAction
from datetime import datetime
import requests
import random
import shutil
import os


def module_init(gd):
    global path, extensions, nyapath, files
    path = gd.config["path"]
    extensions = gd.config["extensions"]
    commands_nyameme = gd.config["commands_nyameme"]
    commands_animeme = gd.config["commands_animeme"]
    nyapath = gd.config["nyapath"]
    for command in commands_nyameme:
        gd.dp.add_handler(PrefixHandler("/", command, nyameme))
    for command in commands_animeme:
        gd.dp.add_handler(PrefixHandler("/", command, animeme))


@run_async
@logging_decorator("nyameme")
def nyameme(update, context):
    filename = datetime.now().strftime("%d%m%y-%H%M%S%f")
    update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
    font, args = get_font(context.args)
    meme_text = get_text(update, args)
    top_text, bottom_text = text_split(meme_text)
    random_image = random.choice(files)
    filename = random_image.split(".")[0]
    extension = "."+random_image.split(".")[1]
    if extension not in extensions:
        update.message.reply_text("Unexpected error")
        return
    shutil.copy(nyapath+random_image, path+random_image)
    update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
    make_meme(top_text, bottom_text, filename, extension, path, font)
    with open(path + filename+"-meme" + extension, "rb") as f:
        update.message.reply_photo(f)
    os.remove(path+filename+extension)
    os.remove(path+filename+"-meme"+extension)
    return


@run_async
@logging_decorator("animeme")
def animeme(update, context):
    filename = datetime.now().strftime("%d%m%y-%H%M%S%f")
    update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
    font, args = get_font(context.args)
    meme_text = get_text(update, args)
    top_text, bottom_text = text_split(meme_text)
    _, _, sample_link = get_image("rating:safe", yandere_request_link, "")
    extension = "."+sample_link.split(".")[-1]
    if extension not in extensions:
        update.message.reply_text("Unexpected error")
        return
    response = requests.get(sample_link, proxies=proxies)
    with open(path+filename+extension, "wb") as img:
        img.write(response.content)
    update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
    make_meme(top_text, bottom_text, filename, extension, path, font)
    with open(path + filename+"-meme" + extension, "rb") as f:
        update.message.reply_photo(f)
    os.remove(path+filename+extension)
    os.remove(path+filename+"-meme"+extension)
    return


def get_text(update, args):
    reply = update.message.reply_to_message
    if reply:
        if reply.caption:
            args = reply.caption
        elif reply.text:
            args = reply.text
        else:
            args = " ".join(args)
        args = args.split(" ")
    else:
        pass
    if len(args) < 1:
        update.message.reply_text("Type in some text!")
        return None
    return args


def text_split(text_list):
    if text_list == None:
        return
    if len(text_list) == 1:
        top_text = None
        bottom_text = text_list[0]
    elif "@" in text_list:
        split_text = " ".join(text_list).split("@", maxsplit=1)
        top_text, bottom_text = text_format(split_text)
    else:
        split_spot = random.randint(1, len(text_list)-1)
        top_text = " ".join(text_list[:split_spot])
        bottom_text = " ".join(text_list[split_spot:])
    return top_text, bottom_text


def get_font(args):
    rand_font = random.choice(list(fonts_dict))
    font = fonts_dict[rand_font]
    if len(args) < 1:
        return font, args
    else:
        for i in fonts_dict:
            if "-"+i in args[0] or "-"+i[0] in args[0]:
                font = fonts_dict[i]
                args = args[1:]
                break
    return font, args