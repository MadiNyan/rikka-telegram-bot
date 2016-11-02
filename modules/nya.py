from telegram.ext import CommandHandler
from telegram import ChatAction
from random import randint
import datetime
import yaml
import os


def handler(dp):
    dp.add_handler(CommandHandler("nya", nya))

# import paths
with open("config.yml", "r") as f:
    nya_folder = yaml.load(f)["path"]["nya"]

files = os.listdir(nya_folder)
filecount = len(files)
print("Nya images: ", filecount)


def nya(bot, update):
    update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
    rand = randint(0, filecount-1)
    result = files[rand]
    with open(nya_folder+"/"+str(result), "rb") as f:
        update.message.reply_photo(f)
    print(datetime.datetime.now(), ">>>", "Sent nya", ">>>", update.message.from_user.username)
