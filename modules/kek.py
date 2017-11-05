#!/usr/bin/python
# -*- coding: utf-8 -*-
from modules.utils import caption_filter, get_image, send_image
from telegram.ext import CommandHandler, MessageHandler
from modules.logging import log_command
from telegram import ChatAction
from datetime import datetime
import subprocess
import os


def module_init(gd):
    global path, extensions
    path = gd.config["path"]
    extensions = gd.config["extensions"]
    commands = gd.config["commands"]
    for command in commands:
        gd.dp.add_handler(MessageHandler(caption_filter("/"+command), kek))
        gd.dp.add_handler(CommandHandler(command, kek))


# get image, pass parameter
def kek(bot, update):
    current_time = datetime.strftime(datetime.now(), "%d.%m.%Y %H:%M:%S")
    filename = datetime.now().strftime("%d%m%y-%H%M%S%f")
    if update.message.reply_to_message is not None:
        kek_param = "".join(update.message.text[5:7])
    elif update.message.caption is not None:
        kek_param = "".join(update.message.caption[5:7])
    else:
        update.message.reply_text("You need an image for that!")
        return
    try:
        extension = get_image(bot, update, path, filename)
    except:
        update.message.reply_text("Can't get the image! :(")
        return
    if extension not in extensions:
        update.message.reply_text("Unsupported file, onii-chan!")
        return False
    update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
    result = kekify(update, kek_param, filename, extension)
    send_image(update, path, result, extension)
    print(current_time, ">", "/kek", ">", update.message.from_user.username)
    log_command(bot, update, current_time, "kek")


# kek process + send
def kekify(update, kek_param, filename, extension):
    if kek_param == "-m":
        result = multikek(update, filename, extension)
        return result
    try:
        kek_dict = get_values(kek_param, path, filename, extension)
        cut = "convert " + path + filename + extension + " -crop " + kek_dict[0] + " " + path + "result" + extension
        subprocess.run(cut, shell=True)
        mirror = "convert " + kek_dict[1] + " " + kek_dict[4] + " " + kek_dict[2]
        subprocess.run(mirror, shell=True)
        if kek_dict[3] == "r":
            kek_dict[1], kek_dict[2] = kek_dict[2], kek_dict[1]
        append = "convert " + kek_dict[1] + " " + kek_dict[2] + " " + kek_dict[5] + " " + path + kek_dict[6] + extension
        subprocess.run(append, shell=True)
        result = kek_dict[6]
        os.remove(path+"result-0"+extension)
        os.remove(path+"result-1"+extension)
        return result
    except:
        update.message.reply_text("Unknown kek parameter.\nUse -l, -r, -t, -b or -m")
        return


def multikek(update, filename, extension):
    kekify(update, "-l", filename, extension)
    kekify(update, "-r", filename, extension)
    kekify(update, "-t", filename, extension)
    kekify(update, "-b", filename, extension)
    append_lr = "convert " + path + filename+ "-kek-left" + extension + " " + path + filename + "-kek-right" + extension + " +append " + path +  filename + "-kek-lr-temp" + extension
    subprocess.run(append_lr, shell=True)
    append_tb = "convert " + path + filename + "-kek-top" + extension + " " + path + filename + "-kek-bot" + extension + " +append " + path + filename + "-kek-tb-temp" + extension
    subprocess.run(append_tb, shell=True)
    append_all = "convert " + path + filename + "-kek-lr-temp" + extension + " " + path + filename + "-kek-tb-temp" + extension + " -append " + path + filename + "-multikek" + extension
    subprocess.run(append_all, shell=True)
    result = filename + "-multikek"
    os.remove(path+filename+"-kek-left"+extension)
    os.remove(path+filename+"-kek-right"+extension)
    os.remove(path+filename+"-kek-top"+extension)
    os.remove(path+filename+"-kek-bot"+extension)
    os.remove(path+filename+"-kek-lr-temp"+extension)
    os.remove(path+filename+"-kek-tb-temp"+extension)
    return result


def get_values(kek_param, path, filename, extension):
    res1 = path + "result-0" + extension
    res2 = path + "result-1" + extension
    parameters = {
        "":   ["50%x100%", res1, res2, "s", "-flop", "+append", filename+"-kek-left"],
        "-l": ["50%x100%", res1, res2, "s", "-flop", "+append", filename+"-kek-left"],
        "-r": ["50%x100%", res2, res1, "r", "-flop", "+append", filename+"-kek-right"],
        "-t": ["100%x50%", res1, res2, "s", "-flip", "-append", filename+"-kek-top"],
        "-b": ["100%x50%", res2, res1, "r", "-flip", "-append", filename+"-kek-bot"]
        }
    return parameters[kek_param]
