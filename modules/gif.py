import os, datetime
from random import randint
from os import listdir
from os.path import isfile, join

def gif(bot, update, args):
    folders = os.walk('gifs')
    found = None
    args = str(args)[2:-2]
    avail_folders = ", ".join(next(folders)[1])
    if args == "help"or args == "?":
        help_gif = "Available folders for /gif request are:\n" + str(avail_folders)
        bot.sendMessage(update.message.chat_id, text=help_gif, reply_to_message_id=update.message.message_id)
        print(datetime.datetime.now(), ">>>", "Gif Help", ">>>", update.message.from_user.username)
    else:
        try:
            for i in folders:
                if i == args:
                    found = args
                    break
            dir = "gifs/"+args
            gifs = [f for f in listdir(dir) if isfile(join(dir, f))]
            filecount = len(gifs)
            rand = randint(0, filecount-1)
            result = list(gifs)[rand]
            with open(dir+"/"+str(result), "rb") as f:
                bot.sendDocument(update.message.chat_id, f, reply_to_message_id=update.message.message_id)
            print(datetime.datetime.now(), ">>>", "Sent gif", ">>>", update.message.from_user.username, ">", result)
        except:
            bot.sendMessage(update.message.chat_id, text="No such folder, try /gif help", reply_to_message_id=update.message.message_id)