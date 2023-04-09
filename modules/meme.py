import os
from datetime import datetime

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import MessageHandler, PrefixHandler

from modules.logging import logging_decorator
from modules.memegenerator import make_meme
from modules.utils import Caption_Filter, get_image, send_image


def module_init(gd):
    global path, extensions, fonts_dict
    path = gd.config["path"]
    extensions = gd.config["extensions"]
    commands = gd.config["commands"]
    fonts_dict = {}
    for i in gd.config["fonts"]:
        fonts_dict[gd.config["fonts"][i]["name"]] = gd.config["fonts"][i]["path"]
    for command in commands:
        # caption_filter = Caption_Filter("/"+command)
        # gd.application.add_handler(MessageHandler(caption_filter, meme))
        gd.application.add_handler(PrefixHandler("/", commands, meme))


def text_format(split_text):
    if len(split_text) == 1 and split_text[0] == "":
        return None, None
    elif len(split_text) > 1 and split_text[0] == "" and split_text[1] == "":
        return None, None
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


@logging_decorator("meme")
async def meme(update: Update, context):
    if update.message is None: return
    filename = datetime.now().strftime("%d%m%y-%H%M%S%f")
    if len(update.message.photo) > 0:
        args = update.message.caption.split(" ")
    else:
        args = update.message.text.split(" ")
    args = args[1:]
    if len(args) < 1:
        await update.message.reply_text("Type in some text!")
        return
    font = fonts_dict["impact"]
    for i in fonts_dict:
        if "-"+i in args[0] or "-"+i[0] in args[0]:
            font = fonts_dict[i]
            args = args[1:]
            break
    if len(args) < 1:
        await update.message.reply_text("Type in some text!")
        return
    initial_text = " ".join(args)
    split_text = initial_text.split("@", maxsplit=1)
    await update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
    try:
        extension = await get_image(update, context, path, filename)
    except:
        await update.message.reply_text("Can't get the image! :(")
        return
    if extension not in extensions:
        await update.message.reply_text("Unsupported file, onii-chan!")
        return

    top_text, bottom_text = text_format(split_text)
    if top_text is None and bottom_text is None:
        await update.message.reply_text("Type in some text!")
        return
    make_meme(top_text, bottom_text, filename, extension, path, font)
    await send_image(update, path, filename+"-meme", extension)
    os.remove(path+filename+extension)
    os.remove(path+filename+"-meme"+extension)
