import importlib
import os

import yaml
from telegram import Update
from telegram.ext import Application, CommandHandler

from modules.logging import logging_decorator

# Import logo from a text file
with open("resources/logo.txt", "r", encoding="UTF-8") as logo_file:
    logo = logo_file.read()
    print(logo)

# Load configs & create folders
with open("config.yml", "r") as f:
    config = yaml.load(f, Loader=yaml.SafeLoader)
key = config["keys"]["telegram_token"]

application = Application.builder().token(key).concurrent_updates(10).build()

class Globals:
    def __init__(self, application, config, full_config):
        self.application = application
        self.config = config
        self.full_config = full_config


for feature in config["features"]:
    if "path" in config["features"][feature]:
        path = config["features"][feature]["path"]
        if not os.path.exists(path):
            os.makedirs(path)
    if config["features"][feature]["enabled"] is True:
        module_config = config["features"][feature]
        global_data = gd = Globals(application, module_config, config)
        module = importlib.import_module("modules." + feature).module_init(gd)
        print(feature)
print("========")

# Import /help from a text file
with open("resources/help.txt", "r", encoding="UTF-8") as helpfile:
    help_text = helpfile.read()


# Start feature
@logging_decorator("start")
async def start(update: Update, context):
    if update.message is None: return
    if update.message.chat.type != "private":
        return
    with open("resources/hello.webp", "rb") as hello:
        await update.message.reply_sticker(hello, quote=False)
    if update.message.from_user:
        personname = update.message.from_user.first_name 
        await update.message.reply_text("Hello, " + personname + "! \nMy name is Rikka! \
                                \nUse /help to see what I can do!", quote=False)
application.add_handler(CommandHandler('start', start))


# Show help
@logging_decorator("help")
async def help(update: Update, context):
    if update.message is None: return
    await context.bot.send_message(update.message.chat_id, help_text, parse_mode="Markdown")
application.add_handler(CommandHandler("help", help))

# Starting bot
application.run_polling()
