#!/usr/bin/python
# -*- coding: utf-8 -*-
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from modules.get_image import get_image
import modules.instagram_filters
import inspect
import yaml
import datetime

# import path
with open("config.yml", "r") as f:
    instagram_folder = yaml.load(f)["path"]["instagram"]

filters = []
all_funcs = inspect.getmembers(modules.instagram_filters, inspect.isfunction)
for i in range(0, len(all_funcs)):
    if all_funcs[i][0].startswith("filt_"):
        filters.append(all_funcs[i][0])


def instagram(bot, update):
    try:
        get_image(bot, update, instagram_folder)
    except:
        update.message.reply_text("I can't get the image! :(")
        return
    instagram_key_list = []
    for i in filters:
        instagram_key = InlineKeyboardButton(str(i)[5:], callback_data=i)
        instagram_key_list.append(instagram_key)
    row_split = lambda list, size, acc=[]: (row_split(list[size:], size, acc + [list[:size]]) if list else acc)
    rows = row_split(instagram_key_list, 3)
    instagram_keyboard = rows
    instagram_reply_markup = InlineKeyboardMarkup(instagram_keyboard)
    update.message.reply_text("Available filters are:", reply_markup=instagram_reply_markup)


def instagram_button(bot, update):
    instagram_query = update.callback_query
    chosen_filter = update.callback_query.data
    filter_name = str(chosen_filter)[5:]
    bot.editMessageText(text="Selected filter: %s\nProcessing..."
                        % filter_name,
                        chat_id=instagram_query.message.chat_id,
                        message_id=instagram_query.message.message_id)
    try:
        getattr(modules.instagram_filters, chosen_filter)(instagram_folder)
    except:
        raise Exception("Instagram error")
    with open(instagram_folder + filter_name + ".jpg", "rb") as f:
        bot.sendPhoto(instagram_query.message.chat_id, f)
    print (datetime.datetime.now(), ">>>", "Sent instagram photo", ">>>", instagram_query.message.from_user.username)
