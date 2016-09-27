from functools import reduce
import datetime

def leet(bot, update, args):
    if update.message.reply_to_message is not None:
        args = update.message.reply_to_message.text
        args = args.split(" ")
    text_leet = ' '.join(args).lower()
    print(text_leet)
    replace_dict = []
    with open("resources/leetdict.txt", "r") as file:
        for i in file.readlines():
            tmp = i.split(",")
            try:
                replace_dict.append((tmp[0], tmp[1]))
            except:pass
    text_leet = reduce(lambda a, kv: a.replace(*kv), replace_dict, text_leet)
    bot.sendMessage(chat_id=update.message.chat_id, text=text_leet, reply_to_message_id=update.message.message_id)
    print(datetime.datetime.now(), ">>>", "Done leetspeak", ">>>", update.message.from_user.username)