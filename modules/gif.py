import os, datetime, yaml
from random import randint
from os import listdir
from os.path import isfile, join
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

def gif(bot, update, args):
    with open('config.yml', 'r') as f:
        gif_folder = yaml.load(f)["path"]["gifs"]
    folders = os.walk(gif_folder)
    found = None
    args = str(args)[2:-2]
    avail_folders = ", ".join(next(folders)[1])
    if args == "help"or args == "?":
        key_values = avail_folders.split(", ")
        key_list = []
        for i in key_values:
            key = InlineKeyboardButton(i, callback_data=i)
            key_list.append(key)
        row_split = lambda list, size, acc=[]: row_split(list[size:], size, acc+[(list[:size])]) if list else acc
        rows = row_split(key_list, 5)
        root_btn = [InlineKeyboardButton("[unsorted]", callback_data="\\")]
        rows.insert(0, root_btn)
        keyboard = rows
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('Available folders for /gif are:', reply_markup=reply_markup)
    else:
        dir = gif_folder+args
        gifs = [f for f in listdir(dir) if isfile(join(dir, f)) and not f.endswith(".db")]
        filecount = len(gifs)
        rand = randint(0, filecount-1)
        result = list(gifs)[rand]
        with open(dir+"/"+str(result), "rb") as f:
            bot.sendDocument(update.message.chat_id, f, reply_to_message_id=update.message.message_id)
        print(datetime.datetime.now(), ">>>", "Sent gif", ">>>", update.message.from_user.username, ">", result)

def gif_button(bot, update):
    query = update.callback_query
    bot.editMessageText(text="Selected option: %s\nUploading can take a while!" % query.data,
                        chat_id=query.message.chat_id,
                        message_id=query.message.message_id)
    dir = "gifs/"+query.data
    gifs = [f for f in listdir(dir) if isfile(join(dir, f))]
    filecount = len(gifs)
    rand = randint(0, filecount-1)
    result = list(gifs)[rand]
    with open(dir+"/"+str(result), "rb") as f:
        bot.sendDocument(query.message.chat_id, f)
    print(datetime.datetime.now(), ">>>", "Sent gif", ">>>", query.message.from_user.username, ">", result)
