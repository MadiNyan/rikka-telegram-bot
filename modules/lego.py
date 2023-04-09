import os
import subprocess
from datetime import datetime

import legofy
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import MessageHandler, PrefixHandler, filters

from modules.logging import logging_decorator
from modules.utils import get_image, get_param, send_image


def module_init(gd):
    global path, extensions
    path = gd.config["path"]
    extensions = gd.config["extensions"]
    commands = gd.config["commands"]
    for command in commands:
        gd.application.add_handler(MessageHandler(filters.PHOTO & filters.CaptionRegex(r'/'+command+''), lego))
        gd.application.add_handler(PrefixHandler("/", command, lego))


@logging_decorator("lego")
async def lego(update: Update, context):
    if update.message is None: return
    filename = datetime.now().strftime("%d%m%y-%H%M%S%f")
    size = await get_param(update, 50, 1, 100)
    if size is None:
        return
    try:
        extension = await get_image(update, context, path, filename)
    except:
        await update.message.reply_text("Can't get the image! :(")
        return
    if extension not in extensions:
        await update.message.reply_text("Unsupported file, onii-chan!")
        return False
    await update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
    if extension == ".webp" or ".png":
        stick = "convert " + path + filename + extension + " -background white -flatten " + path + filename + extension
        subprocess.run(stick, shell=True)
    legofy.main(image_path=path + filename + extension,
                output_path=path + filename + "-lego" + extension,
                size=size, palette_mode=None, dither=False)
    await send_image(update, path, filename+"-lego", extension)
    os.remove(path+filename+extension)
    os.remove(path+filename+"-lego"+extension)
