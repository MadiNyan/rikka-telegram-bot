from functools import reduce

from telegram import Update
from telegram.ext import PrefixHandler

from modules.logging import logging_decorator


def module_init(gd):
    global leet_dictionary, extensions
    leet_dictionary = gd.config["leet_dictionary"]
    commands = gd.config["commands"]
    for command in commands:
        gd.application.add_handler(PrefixHandler("/", command, leet))


@logging_decorator("leet")
async def leet(update: Update, context):
    if update.message is None:
        return

    args = " ".join(context.args)

    # Check if the message is a reply
    if update.message.reply_to_message is not None:
        reply = update.message.reply_to_message
        if len(reply.photo) > 0:
            # If the reply has a photo, use the caption as the args
            args = reply.caption
        else:
            # Otherwise, use the text of the reply as the args
            args = reply.text

    if args is None:
        await update.message.reply_text("Type in some text!")
        return

    text_leet = args.lower()

    if text_leet == "":
        return

    replace_dict = []
    with open(leet_dictionary, "r", encoding="UTF-8") as file:
        for line in file:
            # Read each line from the leet_dictionary file
            tmp = line.split(",")
            try:
                # Try to split the line into key-value pairs
                replace_dict.append((tmp[0], tmp[1]))
            except IndexError:
                # Ignore lines that do not contain a comma for key-value pairs
                pass

    # Replace leet characters in the text_leet string
    text_leet = reduce(lambda a, kv: a.replace(*kv), replace_dict, text_leet)

    # Reply with the converted text_leet string
    await update.message.reply_text(text_leet)

