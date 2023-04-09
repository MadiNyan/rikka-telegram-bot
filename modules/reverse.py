import asyncio
import os
from datetime import datetime

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import MessageHandler, PrefixHandler

from modules.logging import logging_decorator
from modules.utils import get_image, send_image


def module_init(gd):
    global path
    path = gd.config["path"]
    commands = gd.config["commands"]
    for command in commands:
        gd.application.add_handler(PrefixHandler("/", command, reverse))


@logging_decorator("reverse")
async def reverse(update: Update, context):
    if update.message is None: return
    filename = datetime.now().strftime("%d%m%y-%H%M%S%f")
    try:
        extension = await get_image(update, context, path, filename)
    except:
        await update.message.reply_text("Can't get the video")
        return
    await update.message.chat.send_action(ChatAction.UPLOAD_VIDEO)
    video = await reverse_video(path, filename, extension)
    await send_image(update, path, video, extension)
    os.remove(path+filename+extension)
    os.remove(path+video+extension)



async def reverse_video(path, filename, extension):
    new_name = "reversed"
    args = f"ffmpeg -loglevel panic -i {path}{filename}{extension} -vf reverse -af areverse {path}reversed{extension} -y"
    process = await asyncio.create_subprocess_shell(args)
    await process.communicate()
    return new_name
