from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from random import randint
import os
import datetime
import logging
import yaml
import re

with open("config.yml", "r") as f:
    key = yaml.load(f)["keys"]["telegram_token"]
updater = Updater(token=key)
dp = updater.dispatcher
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# Import /help from a text file
with open("resources/help.txt", "r") as helpfile:
    help_text = helpfile.read()
    print("Help textfile imported successfully")


# custom filters
def caption_filter(text):
    return lambda msg: bool(msg.photo) and msg.caption.startswith(text)


def text_filter(text):
    return lambda msg: bool(text in msg.text)


# All the feature functions go here:
# start feature
def start(bot, update):
    with open("resources/hello.webp", "rb") as hello:
        update.message.reply_sticker(hello, quote=False)
    personname = update.message.from_user.first_name
    update.message.reply_text("Konnichiwa, " + personname + "! \nMy name is Takanashi Rikka desu! \
                              \nUse /help to see what I can do! :3", quote=False)
    print(datetime.datetime.now(), ">>>", "Done /start", ">>>", update.message.from_user.username)


# show help
def help(bot, update):
    update.message.reply_text(help_text)
    print(datetime.datetime.now(), ">>>", "Done /help", ">>>", update.message.from_user.username)

# leetspeak convert
from modules.leetspeak import leet
print("1337 imported")

# tori stats
from modules.toribash import toristats
print("Toristats imported")

# roll
from modules.roll import roll
print("Roll imported")

# Glitch image
from modules.glitch import glitch
print("Glitch imported")

# Legofy image
from modules.lego import lego
print("Lego imported")

# reply with Kappa
from modules.kappa import kappa
print("Kappa imported")

# post random gif
from modules.gif import gif, gif_button
print("Gif imported")

# meme creator
from modules.meme import meme
print("Memes imported")

# nyan girls
from modules.nya import nya
print("Nya imported")

# server status
from modules.pcstat import status
print("Status imported")

# Bing image search
from modules.bing_search import img_search, vid_search, news_search
print("Bing search imported")

# Kek images
from modules.kek import kek
print("Kek imported")

# Instagram
from modules.instagram import instagram, instagram_button
print("Instagram imported")

# Anime search
from modules.anime import anime, get_anime
print("Anime imported")

# All the handlers for feature functions go here:
dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("help", help))
dp.add_handler(CommandHandler("leet", leet, pass_args=True))
dp.add_handler(CommandHandler("toribash", toristats, pass_args=True))
dp.add_handler(CommandHandler("roll", roll, pass_args=True))
dp.add_handler(MessageHandler(caption_filter("/glitch"), glitch))
dp.add_handler(CommandHandler("glitch", glitch))
dp.add_handler(MessageHandler(caption_filter("/lego"), lego))
dp.add_handler(CommandHandler("lego", lego))
dp.add_handler(CommandHandler("gif", gif, pass_args=True))
dp.add_handler(MessageHandler(caption_filter("/meme"), meme))
dp.add_handler(CommandHandler("meme", meme))
dp.add_handler(CommandHandler("nya", nya))
dp.add_handler(CommandHandler("status", status))
dp.add_handler(CommandHandler("img", img_search, pass_args=True))
dp.add_handler(CommandHandler("vid", vid_search, pass_args=True))
dp.add_handler(CommandHandler("news", news_search, pass_args=True))
dp.add_handler(MessageHandler(caption_filter("/kek"), kek))
dp.add_handler(CommandHandler("kek", kek))
dp.add_handler(MessageHandler(caption_filter("/instagram"), instagram))
dp.add_handler(CommandHandler("instagram", instagram))
dp.add_handler(CommandHandler("a", anime, pass_args=True))
dp.add_handler(MessageHandler(Filters.text, kappa))

dp.add_handler(CallbackQueryHandler(instagram_button, pattern="(filt_)\w+"))
dp.add_handler(CallbackQueryHandler(gif_button, pattern="([A-z0-9\\\])"))

# Starting bot
updater.start_polling(clean=True)
# Run the bot until you presses Ctrl+C
print("=====================\nUp and running!\n")
updater.idle()
