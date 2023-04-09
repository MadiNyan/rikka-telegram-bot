import os
from datetime import datetime

import comtypes.client
from pythoncom import CoInitialize, CoUninitialize
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import PrefixHandler

from modules.logging import logging_decorator


def module_init(gd):
    global path
    path = gd.config["path"]
    commands = gd.config["commands"]
    for command in commands:
        gd.application.add_handler(PrefixHandler("/", command, tts))


@logging_decorator("say")
async def tts(update: Update, context):
    if update.message is None: return
    filename = datetime.now().strftime("%d%m%y-%H%M%S%f")
    reply = update.message.reply_to_message
    if reply is None:
        text = "".join(context.args)
    elif reply.text is not None:
        text = reply.text
    else:
        return
    if len(text) == 0:
        await update.message.reply_text("Type in some text ^^")
        return
    await update.message.chat.send_action(ChatAction.RECORD_VOICE)
    CoInitialize()
    speak = comtypes.client.CreateObject("SAPI.SpVoice")
    filestream = comtypes.client.CreateObject("SAPI.spFileStream")
    filestream.open(path+filename+".ogg", 3, False)
    speak.AudioOutputStream = filestream 
    speak.Speak(text)
    filestream.close()
    CoUninitialize()
    with open(path + filename + ".ogg", "rb") as speech:
        await update.message.reply_voice(speech, quote=False)
    os.remove(path+filename+".ogg")
