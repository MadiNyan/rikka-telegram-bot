#!/usr/bin/python
# -*- coding: utf-8 -*-
from modules.logging import logging_decorator
from pythoncom import CoInitialize, CoUninitialize
from telegram.ext import CommandHandler
from telegram import ChatAction
from datetime import datetime
import comtypes.client
import os


def module_init(gd):
    global path
    path = gd.config["path"]
    commands = gd.config["commands"]
    for command in commands:
        gd.dp.add_handler(CommandHandler(command, tts, pass_args=True))


@logging_decorator("say")
def tts(bot, update, args):
    filename = datetime.now().strftime("%d%m%y-%H%M%S%f")
    reply = update.message.reply_to_message
    if reply is None:
        text = "".join(args)
    elif reply.text is not None:
        text = reply.text
    else:
        return
    if len(text) == 0:
        update.message.reply_text("Type in some text ^^")
        return
    update.message.chat.send_action(ChatAction.RECORD_AUDIO)
    CoInitialize()
    speak = comtypes.client.CreateObject("SAPI.SpVoice")
    filestream = comtypes.client.CreateObject("SAPI.spFileStream")
    filestream.open(path+filename+".ogg", 3, False)
    speak.AudioOutputStream = filestream 
    speak.Speak(text)
    filestream.close()
    CoUninitialize()
    with open(path + filename + ".ogg", "rb") as speech:
        update.message.reply_voice(speech, quote=False)
    os.remove(path+filename+".ogg")
