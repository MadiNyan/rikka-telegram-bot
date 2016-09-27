import os, datetime
from random import randint

dir = "nya"
files = os.listdir(dir)
filecount = len(files)

print("Nyan images: ", filecount)

def nya(bot, update):
    rand = randint(0, filecount-1)
    result = files[rand]
    with open(dir+"/"+str(result), "rb") as f:
        bot.sendPhoto(update.message.chat_id, f, reply_to_message_id=update.message.message_id)
    print(datetime.datetime.now(), ">>>", "Sent nyan tyan", ">>>", update.message.from_user.username)