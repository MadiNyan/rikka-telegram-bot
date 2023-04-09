import os
from datetime import datetime

from PIL import Image
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
        gd.application.add_handler(MessageHandler(filters.PHOTO & filters.CaptionRegex(r'/'+command+''), jpeg))
        gd.application.add_handler(PrefixHandler("/", command, jpeg))


@logging_decorator("jpeg")
async def jpeg(update: Update, context):
    if update.message is None: return
    filename = datetime.now().strftime("%d%m%y-%H%M%S%f")
    compress = await get_param(update, 6, 1, 10)
    if compress == 0:
        return
    else:
        compress = 11 - compress
    try:
        extension = await get_image(update, context, path, filename)
    except:
        await update.message.reply_text("I can't get the image! :(")
        return
    await update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
    if extension not in extensions:
        await update.message.reply_text("Unsupported file, onii-chan!")
        return

    original = Image.open(path+filename+extension, 'r')
    if extension == ".jpg":
        original.save(path+filename+".jpg",quality=compress,optimize=True)
    else:
        rgb_im = original.convert('RGB')
        rgb_im.save(path+"compressed.jpg",quality=compress,optimize=True)
        foreground = Image.open(path+"compressed.jpg")
        try:
            original.paste(foreground, (0, 0), original)
        except:
            pass  
        original.save(path+filename+extension)
        os.remove(path+"compressed.jpg")
    await send_image(update, path, filename, extension)
    os.remove(path+filename+extension)
