from telegram.ext import CommandHandler
from functools import reduce
import datetime
import yaml

# import path
with open("config.yml", "r") as f:
    leet_dictionary = yaml.load(f)["path"]["leet_dictionary"]


def handler(dp):
    dp.add_handler(CommandHandler("leet", leet, pass_args=True))


def leet(bot, update, args):
    if update.message.reply_to_message is not None:
        args = update.message.reply_to_message.text
        args = args.split(" ")
    text_leet = " ".join(args).lower()
    if text_leet == "":
        return
    replace_dict = []
    with open(leet_dictionary, "r") as file:
        for i in file.readlines():
            tmp = i.split(",")
            try:
                replace_dict.append((tmp[0], tmp[1]))
            except:
                pass
    text_leet = reduce(lambda a, kv: a.replace(*kv), replace_dict, text_leet)
    update.message.reply_text(text_leet)
    print(datetime.datetime.now(), ">>>", "Done leetspeak", ">>>", update.message.from_user.username)
