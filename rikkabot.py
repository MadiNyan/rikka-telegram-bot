from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from random import randint
import os, datetime, logging, yaml

with open('config.yml', 'r') as f:
    key = yaml.load(f)["keys"]["telegram_token"]
updater = Updater(token=key)
dp = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Import /help from a text file
helpfile = open("resources/help.txt","r")
help_text = helpfile.read()
print("Help textfile imported successfully")
helpfile.close()

# custom filters
def caption_filter(text):
    return lambda msg: bool(msg.photo) and msg.caption.startswith(text)
    
def text_filter(text):
    return lambda msg: bool(text in msg.text)

### All the feature functions go here:
# start feature
def start(bot, update):
    with open("resources/hello.webp", "rb") as hello:
        bot.sendSticker(update.message.chat_id, hello)
    personname = update.message.from_user.first_name
    bot.sendMessage(chat_id=update.message.chat_id, text="Konnichiwa, " + personname + "! \nMy name is Takanashi Rikka desu! \nUse /help to see what I can do! :3")
    print(datetime.datetime.now(), ">>>", "Done /start", ">>>", update.message.from_user.username)

# show help
def help(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text=help_text)
    print(datetime.datetime.now(), ">>>", "Done /help", ">>>", update.message.from_user.username)

# caps all the text
from modules.caps import caps
print("Caps imported")

#leetspeak convert
from modules.leetspeak import leet
print("1337 imported")

#tori stats
from modules.toribash import toristats
print("Toristats imported")

# roll
from modules.roll import roll
print("Or imported")

# Glitch image
from modules.glitch import glitch
print("Glitch imported")

# Legofy image
from modules.lego import lego
print("Lego imported")

# reply with Kappa
from modules.kappa import kappa
print("Kappa imported")

# reply with Nutshack
from modules.nutshack import nutshack
print("Nutshack imported")
    
# post random gif
from modules.gif import gif
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

### All the handlers for feature functions go here:
dp.add_handler(CommandHandler('start', start))
dp.add_handler(CommandHandler("help", help))
dp.add_handler(CommandHandler('caps', caps, pass_args=True))
dp.add_handler(CommandHandler('leet', leet, pass_args=True))
dp.add_handler(CommandHandler('toribash', toristats, pass_args=True))
dp.add_handler(CommandHandler('roll', roll, pass_args=True))
dp.add_handler(MessageHandler([text_filter("Kappa")], kappa))
dp.add_handler(MessageHandler([text_filter("kappa")], kappa))
dp.add_handler(MessageHandler([text_filter("каппа")], kappa))
dp.add_handler(MessageHandler([text_filter("Каппа")], kappa))
dp.add_handler(MessageHandler([caption_filter("/glitch")], glitch))
dp.add_handler(CommandHandler('glitch', glitch))
dp.add_handler(MessageHandler([caption_filter("/lego")], lego))
dp.add_handler(CommandHandler('lego', lego))
dp.add_handler(CommandHandler('gif', gif, pass_args=True))
dp.add_handler(MessageHandler([caption_filter("/meme")], meme))
dp.add_handler(CommandHandler('meme', meme))
dp.add_handler(CommandHandler('nya', nya))
dp.add_handler(CommandHandler('status', status))
dp.add_handler(CommandHandler('img', img_search, pass_args=True))
dp.add_handler(CommandHandler('vid', vid_search, pass_args=True))
dp.add_handler(CommandHandler('news', news_search, pass_args=True))
dp.add_handler(MessageHandler([Filters.text], nutshack))

# Starting bot
updater.start_polling()
# Run the bot until the you presses Ctrl+C
print("=====================\nUp and running!\n")
updater.idle()
