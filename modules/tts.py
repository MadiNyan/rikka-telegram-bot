#!/usr/bin/python
# -*- coding: utf-8 -*-
from telegram.ext import CommandHandler
from telegram import ChatAction
from gtts import gTTS
import datetime


def module_init(gd):
    global path
    path = gd.config["path"]
    commands = gd.config["commands"]
    for command in commands:
        gd.dp.add_handler(CommandHandler(command, tts, pass_args=True))


def tts(bot, update, args):
    reply = update.message.reply_to_message
    if reply is None:
        text = "".join(args)
    elif reply.text is not None:
        text = reply.text
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