#!/usr/bin/python
# -*- coding: utf-8 -*-
from telegram.ext import CommandHandler
from random import randint, seed
import datetime
import zlib

choices = ["🎱 It is certain", "🎱 It is decidedly so", "🎱 Without a doubt", "🎱 Yes definitely",
           "🎱 You may rely on it", "🎱 As I see it, yes", "🎱 Most likely", "🎱 Outlook good", 
           "🎱 Yes", "🎱 Signs point to yes", "🎱 Reply hazy try again", "🎱 Ask again later",
           "🎱 Better not tell you now", "🎱 Cannot predict now", "🎱 Concentrate and ask again", 
           "🎱 Don't count on it", "🎱 My reply is no", "🎱 My sources say no", "🎱 Outlook not so good", 
           "🎱 Very doubtful"]


def handler(dp):
    dp.add_handler(CommandHandler("roll", roll, pass_args=True))

def mysteryball(update, string):
    if string is "":
        seed()
    else:
        input_hash = zlib.adler32(string.encode())
        seed(input_hash)
    answer = randint(0, len(choices)-1)
    update.message.reply_text(choices[answer])


def roll(bot, update, args):
    text_roll = ' '.join(args)
    splitter_ru = " или "
    splitter_en = " or "
    if splitter_ru in text_roll:
        split_text = text_roll.split(splitter_ru)
        rolling_process(update, text_roll, split_text)
    elif splitter_en in text_roll:
        split_text = text_roll.split(splitter_en)
        rolling_process(update, text_roll, split_text)
    else:
        mysteryball(update, text_roll)
    print(datetime.datetime.now(), ">>>", "Done /roll", ">>>", update.message.from_user.username)

def rolling_process(update, full_text, split_text):
    input_hash = zlib.adler32(full_text.encode())
    seed(input_hash)
    randoms = len(split_text) - 1
    answer = randint(0, randoms)
    uncapitalized = split_text[answer]
    capitalized = uncapitalized[0].upper() + uncapitalized[1:]
    update.message.reply_text(capitalized)

