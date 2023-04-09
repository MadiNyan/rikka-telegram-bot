import os
import subprocess
from datetime import datetime
from random import randint

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import MessageHandler, PrefixHandler, filters

from modules.logging import logging_decorator
from modules.utils import get_image


def module_init(gd):
    global path, extensions
    path = gd.config["path"]
    extensions = gd.config["extensions"]
    commands = gd.config["commands"]
    for command in commands:
        gd.application.add_handler(MessageHandler(filters.PHOTO & filters.CaptionRegex(r'/'+command+''), glitch))
        gd.application.add_handler(PrefixHandler("/", command, glitch))


@logging_decorator("glitch")
async def glitch(update: Update, context):
    if update.message is None: return
    filename = datetime.now().strftime("%d%m%y-%H%M%S%f")
    try:
        extension = await get_image(update, context, path, filename)
    except:
        await update.message.reply_text("I can't get the image! :(")
        return
    await update.message.chat.send_chat_action(ChatAction.UPLOAD_PHOTO)
    if extension not in extensions:
        await update.message.reply_text("Unsupported file, onii-chan!")
        return False
    jpg = "convert " + path + filename + extension + " -resize 100% " + path + filename + ".jpg"
    subprocess.run(jpg, shell=True)
    await process_img(update, filename)
    os.remove(path+filename+extension)
    os.remove(path+filename+"-glitched.jpg")


async def process_img(update, filename):
    with open(path + filename + ".jpg", "rb") as f:
        linelist = list(f)
        linecount = len(linelist) - 10
        for i in range(5):
            i = randint(1, linecount - 1)
            linecount = linecount - 1
            del linelist[i]
    with open(path + filename + "-glitched" + ".jpg", "w+b") as f:
        for content in linelist:
            f.write(content)
        f.seek(0)
        await update.message.reply_photo(f)
