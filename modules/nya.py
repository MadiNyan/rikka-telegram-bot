import os
import random

from telegram import InputMediaPhoto, Update
from telegram.constants import ChatAction
from telegram.ext import PrefixHandler

from modules.logging import logging_decorator
from modules.utils import get_param


def module_init(gd):
    global path, files, token
    path = gd.config["path"]
    commands = gd.config["commands"]
    token = gd.full_config["keys"]["telegram_token"]
    for command in commands:
        gd.application.add_handler(PrefixHandler("/", command, nya))
    files = os.listdir(path)


@logging_decorator("nya")
async def nya(update: Update, context):
    if update.message is None: return
    await update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
    amount = await get_param(update, 1, 1, 10)
    photos = []
    upload_files = []
    for i in range(amount):
        random_image = random.choice(files)
        upload_files.append(InputMediaPhoto(media=open(path+random_image, "rb")))
    await update.message.reply_media_group(media=upload_files)
    return amount
