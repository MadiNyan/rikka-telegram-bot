import os
from datetime import datetime

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import MessageHandler, PrefixHandler, filters
from wand.image import Image

from modules.logging import logging_decorator
from modules.utils import get_image, get_param, mp4_fix, send_image


def module_init(gd):
    global path
    path = gd.config["path"]
    commands = gd.config["commands"]
    for command in commands:
        gd.application.add_handler(MessageHandler(filters.PHOTO & filters.CaptionRegex(r'/'+command+''), liquid))
        gd.application.add_handler(PrefixHandler("/", command, liquid))
        

@logging_decorator("liq")
async def liquid(update: Update, context):
    if update.message is None: return
    filename = datetime.now().strftime("%d%m%y-%H%M%S%f")
    power = await get_param(update, 60, -100, 100)
    if power is None:
        return
    try:
        extension = await get_image(update, context, path, filename)
    except:
        await update.message.reply_text("I can't get the image! :(")
        return
    power = (100 - (power / 1.3)) / 100
    await update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
    with Image(filename=path+filename+extension) as original:
        w, h = original.size
        new = Image()
        for frame in original.sequence:
            img = Image(image=frame)
            img.liquid_rescale(int(w*power), int(h*power), delta_x =1)
            img.resize(w, h)
            new.sequence.append(img)
            img.close()
        new.save(filename=path+filename+extension)
        if extension == ".mp4":
            filename = mp4_fix(path, filename)
        await send_image(update, path, filename, extension)
        new.close()
        os.remove(path+filename+extension)
