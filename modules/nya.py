import os
import datetime
import yaml
from random import randint

# import paths
with open('config.yml', 'r') as f:
    nya_folder = yaml.load(f)["path"]["nya"]

files = os.listdir(nya_folder)
filecount = len(files)

print("Nyan images: ", filecount)


def nya(bot, update):
    rand = randint(0, filecount-1)
    result = files[rand]
    with open(nya_folder+"/"+str(result), "rb") as f:
        bot.sendPhoto(update.message.chat_id, f, reply_to_message_id=update.message.message_id)
    print(datetime.datetime.now(), ">>>", "Sent nyan tyan", ">>>", update.message.from_user.username)
