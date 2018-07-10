#!/usr/bin/python
# -*- coding: utf-8 -*-
from telegram.ext import CommandHandler
from modules.logging import log_command
from telegram import ChatAction
from datetime import datetime
from gtts import gTTS
import os


def module_init(gd):
    global path
    path = gd.config["path"]
    commands = gd.config["commands"]
    for command in commands:
        gd.dp.add_handler(CommandHandler(command, tts, pass_args=True))


def tts(bot, update, args):
    current_time = datetime.strftime(datetime.now(), "%d.%m.%Y %H:%M:%S")
    filename = datetime.now().strftime("%d%m%y-%H%M%S%f")
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
    tts.save(path + filename + ".mp3")
    with open(path + filename + ".mp3", "rb") as f:
        linelist = list(f)
        linecount = len(linelist)
    if linecount == 1:
        update.message.chat.send_action(ChatAction.RECORD_AUDIO)
        lang = "ru"
        tts = gTTS(text, lang)
        tts.save(path + filename + ".mp3")
    with open(path + filename + ".mp3", "rb") as speech:
        update.message.reply_voice(speech, quote=False)
    print(current_time, ">", "/say", ">", update.message.from_user.username)
    os.remove(path+filename+".mp3")
    log_command(bot, update, current_time, "say")
