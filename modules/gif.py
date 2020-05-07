#!/usr/bin/python
# -*- coding: utf-8 -*-
from modules.logging import logging_decorator, access_decorator
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ChatAction
from telegram.ext import CommandHandler, CallbackQueryHandler
from telegram.ext.dispatcher import run_async
from random import randint
import os


def module_init(gd):
    global path
    path = gd.config["path"]
    commands = gd.config["commands"]
    for command in commands:
        gd.dp.add_handler(CommandHandler(command, gif, pass_args=True))
    gd.dp.add_handler(CallbackQueryHandler(gif_button, pattern="(gif_)\w+"))


@run_async
@logging_decorator("gif")
def gif(bot, update, args):
    folders = os.walk(path)
    args = "gif_" + str(args)[2:-2]
    avail_folders = next(folders)[1]
    if args == "gif_help" or args == "gif_?":
        reply_markup = make_keyboard(avail_folders)
        update.message.reply_text("Available folders for /gif are:", reply_markup=reply_markup)
    elif args in avail_folders:
        update.message.chat.send_action(ChatAction.UPLOAD_DOCUMENT)
        gifs_dir = path + args
        result = getgifs(update, gifs_dir)
        with open(gifs_dir + "/" + str(result), "rb") as f:
            update.message.reply_document(f)
    elif args == "gif_":
        gifs_dir = path
        result = getgifs(update, gifs_dir)
        with open(gifs_dir + "/" + str(result), "rb") as f:
            update.message.reply_document(f)
    else:
        update.message.reply_text("No such folder, try /gif help")
    return args


def gif_button(bot, update):
    query = update.callback_query
    user = query.from_user.username
    display_data = str(query.data)[4:]
    bot.editMessageText(text="%s selected: %s\nUploading can take a while!"
                        % (user, display_data),
                        chat_id=query.message.chat_id,
                        message_id=query.message.message_id)
    query.message.chat.send_action(ChatAction.UPLOAD_DOCUMENT)
    if display_data == "unsorted":
        gifs_dir = path
    else:
        gifs_dir = path + query.data
    result = getgifs(update, gifs_dir)
    with open(gifs_dir + "/" + str(result), "rb") as f:
        bot.sendDocument(query.message.chat_id, f)
    return display_data


def make_keyboard(folders):
    key_list = []
    for i in folders:
        key = InlineKeyboardButton(str(i)[4:], callback_data=i)
        key_list.append(key)
    row_split = lambda list, size, acc=[]: (row_split(list[size:], size, acc + [list[:size]]) if list else acc)
    rows = row_split(key_list, 4)
    root_btn = [InlineKeyboardButton("[unsorted]", callback_data="gif_unsorted")]
    rows.insert(0, root_btn)
    keyboard = rows
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup


def getgifs(update, gifs_dir):
    gifs = [f for f in os.listdir(gifs_dir)
                    if os.path.isfile(os.path.join(gifs_dir, f))
                    and f.endswith((".mp4", ".gif"))]
    filecount = len(gifs)
    rand = randint(0, filecount - 1)
    result = list(gifs)[rand]
    return result
