#!/usr/bin/python
# -*- coding: utf-8 -*-
from telegram.ext import CommandHandler
from telegram import ChatAction
from gtts import gTTS
import datetime
import yaml


def handler(dp):
    dp.add_handler(CommandHandler("say", tts, pass_args=True))

with open("config.yml", "r") as f:
    path = yaml.load(f)["path"]["tts"]


def tts(bot, update, args):
    text = "".join(args)
    if len(text) == 0:
        update.message.reply_text("Type in some text ^^")
        return
    update.message.chat.send_action(ChatAction.RECORD_AUDIO)
    lang="en"
    tts = gTTS(text, lang)
    tts.save(path + "voice.mp3")
    with open(path + "voice.mp3", "rb") as f:
        linelist = list(f)
        linecount = len(linelist)
    if linecount == 1:
        update.message.chat.send_action(ChatAction.RECORD_AUDIO)
        lang = "ru"
        tts = gTTS(text, lang)
        tts.save(path + "voice.mp3")
    with open(path + "voice.mp3", "rb") as speech:
        update.message.reply_voice(speech, quote=False)
    print(datetime.datetime.now(), ">>>", "Done tts", ">>>", update.message.from_user.username)