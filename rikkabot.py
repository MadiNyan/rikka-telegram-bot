#!/usr/bin/python
# -*- coding: utf-8 -*-
from modules.logging import logging_decorator
from telegram.ext import Updater, PrefixHandler
from random import randint
import importlib
import yaml
import os
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)	
logger = logging.getLogger(__name__)	
logging.getLogger("telegram.utils.promise").propagate = False


class Globals:
    def __init__(self, updater, dp, config, full_config):
        self.updater = updater
        self.dp = dp
        self.config = config
        self.full_config = full_config

# Import logo from a text file
with open("resources/logo.txt", "r", encoding="UTF-8") as logo_file:
    logo = logo_file.read()
    print(logo)

# Load configs & create folders
with open("config.yml", "r") as f:
    config = yaml.load(f)
key = config["keys"]["telegram_token"]
updater = Updater(token=key, use_context=True, workers=16)
dp = updater.dispatcher

for feature in config["features"]:
    if "path" in config["features"][feature]:
        path = config["features"][feature]["path"]
        if not os.path.exists(path):
            os.makedirs(path)
    if config["features"][feature]["enabled"] is True:
        module_config = config["features"][feature]
        global_data = gd = Globals(updater, dp, module_config, config)
        module = importlib.import_module("modules." + feature).module_init(gd)
        print(feature)

# Import /help from a text file
with open("resources/help.txt", "r", encoding="UTF-8") as helpfile:
    help_text = helpfile.read()
    print("Help textfile imported")


# Start feature
@logging_decorator("start")
def start(update, context):
    if update.message.chat.type != "private":
        return
    with open("resources/hello.webp", "rb") as hello:
        update.message.reply_sticker(hello, quote=False)
    personname = update.message.from_user.first_name
    update.message.reply_text("Konnichiwa, " + personname + "! \nMy name is Takanashi Rikka desu! \
                              \nUse /help to see what I can do! :3", quote=False)
dp.add_handler(PrefixHandler("/", "start", start))


# Show help
@logging_decorator("help")
def help(update, context):
    context.bot.send_message(update.message.chat_id, help_text, parse_mode="Markdown")
dp.add_handler(PrefixHandler("/", "help", help))

# Starting bot
updater.start_polling(clean=True, timeout=10, bootstrap_retries=-1, poll_interval=0.5, read_latency=2.0)
# Run the bot until you presses Ctrl+C
print("=====================\nUp and running!\n")
#Idle
updater.idle()
