from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from random import randint
import importlib
import datetime
import logging
import yaml
import os
import re

with open("config.yml", "r") as f:
    key = yaml.load(f)["keys"]["telegram_token"]
updater = Updater(token=key)
dp = updater.dispatcher
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)


def load_modules(dp, *modules):
    for i in modules:
        importlib.import_module("modules." + i).handler(dp)
        print(i, "imported")

load_modules(dp,
             "anime",
             "bing_search",
             "instagram",
             "gif",
             "glitch",
             "kappa",
             "kek",
             "leetspeak",
             "lego",
             "liquid",
             "meme",
             "nya",
             "pcstat",
             "roll",
             "toribash")

# Import /help from a text file
with open("resources/help.txt", "r") as helpfile:
    help_text = helpfile.read()
    print("Help textfile imported")


# start feature
def start(bot, update):
    with open("resources/hello.webp", "rb") as hello:
        update.message.reply_sticker(hello, quote=False)
    personname = update.message.from_user.first_name
    update.message.reply_text("Konnichiwa, " + personname + "! \nMy name is Takanashi Rikka desu! \
                              \nUse /help to see what I can do! :3", quote=False)
    print(datetime.datetime.now(), ">>>", "Done /start", ">>>", update.message.from_user.username)
dp.add_handler(CommandHandler("start", start))


# show help
def help(bot, update):
    update.message.reply_text(help_text)
    print(datetime.datetime.now(), ">>>", "Done /help", ">>>", update.message.from_user.username)
dp.add_handler(CommandHandler("help", help))

# Starting bot
updater.start_polling(clean=True)
# Run the bot until you presses Ctrl+C
print("=====================\nUp and running!\n")
updater.idle()
