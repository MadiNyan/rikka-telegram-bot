#!/usr/bin/python
# -*- coding: utf-8 -*-
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ChatAction
from telegram.ext import CommandHandler, CallbackQueryHandler
from random import randint
import datetime
import yaml
import os


def handler(dp):
    dp.add_handler(CommandHandler("gif", gif, pass_args=True))
    dp.add_handler(CallbackQueryHandler(gif_button, pattern="([A-z0-9\\\])"))

with open("config.yml", "r") as f:
    gif_folder = yaml.load(f)["path"]["gifs"]


def gif(bot, update, args):
    folders = os.walk(gif_folder)
    args = str(args)[2:-2]
    avail_folders = next(folders)[1]
    if args == "help" or args == "?":
        key_list = []
        for i in avail_folders:
            key = InlineKeyboardButton(i, callback_data=i)
            key_list.append(key)
        row_split = lambda list, size, acc=[]: (row_split(list[size:], size, acc + [list[:size]]) if list else acc)
        rows = row_split(key_list, 4)
        root_btn = [InlineKeyboardButton("[unsorted]",
                    callback_data="\\")]
        rows.insert(0, root_btn)
        keyboard = rows
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("Available folders for /gif are:", reply_markup=reply_markup)
    elif args in avail_folders or args == "":
        update.message.chat.send_action(ChatAction.UPLOAD_DOCUMENT)
        gifs_dir = gif_folder + args
        gifs = [f for f in os.listdir(gifs_dir)
                if os.path.isfile(os.path.join(gifs_dir, f))
                and f.endswith((".mp4", ".gif"))]
        filecount = len(gifs)
        rand = randint(0, filecount - 1)
        result = list(gifs)[rand]
        with open(gifs_dir + "/" + str(result), "rb") as f:
            update.message.reply_document(f)
        print (datetime.datetime.now(), ">>> Sent gif >>>",
               update.message.from_user.username, ">", result)
    else:
        update.message.reply_text("No such folder, try /gif help")


def gif_button(bot, update):
    query = update.callback_query
    bot.editMessageText(text="Selected option: %s\nUploading can take a while!"
                        % query.data, chat_id=query.message.chat_id,
                        message_id=query.message.message_id)
    query.message.chat.send_action(ChatAction.UPLOAD_DOCUMENT)
    gifs_dir = gif_folder + query.data
    gifs = [f for f in os.listdir(gifs_dir)
            if os.path.isfile(os.path.join(gifs_dir, f))
            and f.endswith((".mp4", ".gif"))]
    filecount = len(gifs)
    rand = randint(0, filecount - 1)
    result = list(gifs)[rand]
    with open(gifs_dir + "/" + str(result), "rb") as f:
        bot.sendDocument(query.message.chat_id, f)
    print (datetime.datetime.now(), ">>> Sent gif >>>",
           query.message.from_user.username, ">", result)
