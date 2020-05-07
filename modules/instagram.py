#!/usr/bin/python
# -*- coding: utf-8 -*-
from modules.logging import logging_decorator
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ChatAction
from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler
from modules.utils import caption_filter, get_image, send_image
import modules.instagram_filters
from datetime import datetime
import inspect
import os


def module_init(gd):
    global path, extensions, filters
    path = gd.config["path"]
    extensions = gd.config["extensions"]
    commands = gd.config["commands"]
    for command in commands:
        gd.dp.add_handler(MessageHandler(caption_filter("/"+command), instagram))
        gd.dp.add_handler(CommandHandler(command, instagram))
    gd.dp.add_handler(CallbackQueryHandler(instagram_button, pattern="(filt_)\w+"))

    filters = []
    all_funcs = inspect.getmembers(modules.instagram_filters, inspect.isfunction)
    for i in range(0, len(all_funcs)):
        if all_funcs[i][0].startswith("filt_"):
            filters.append(all_funcs[i][0])


def instagram(bot, update):
    global filename
    filename = datetime.now().strftime("%d%m%y-%H%M%S%f")
    try:
        extension = get_image(bot, update, path, filename)
    except:
        update.message.reply_text("I can't get the image! :(")
        return
    if extension not in extensions:
        update.message.reply_text("Unsupported file, onii-chan!")
        return False
    instagram_key_list = []
    for i in filters:
        inst_filter = i
        instagram_key = InlineKeyboardButton(str(i)[5:], callback_data=",".join([inst_filter, extension]))
        instagram_key_list.append(instagram_key)
    row_split = lambda list, size, acc=[]: (row_split(list[size:], size, acc + [list[:size]]) if list else acc)
    rows = row_split(instagram_key_list, 3)
    instagram_keyboard = rows
    instagram_reply_markup = InlineKeyboardMarkup(instagram_keyboard)
    update.message.reply_text("Available filters are:", reply_markup=instagram_reply_markup)


@logging_decorator("instagram")
def instagram_button(bot, update):
    query = update.callback_query
    chosen_filter, extension = update.callback_query.data.split(",")
    filter_name = str(chosen_filter)[5:]
    user = query.from_user.username
    bot.editMessageText(text="%s selected: %s\nProcessing..."
                        % (user, filter_name),
                        chat_id=query.message.chat_id,
                        message_id=query.message.message_id)
    query.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
    try:
        getattr(modules.instagram_filters, chosen_filter)(path, filename, extension)
    except:
        raise Exception("Instagram error")
    send_image(query, path, filename+"-"+filter_name, extension)
    os.remove(path+filename+extension)
    os.remove(path+filename+"-"+filter_name+extension)
