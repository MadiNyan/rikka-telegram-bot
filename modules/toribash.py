#!/usr/bin/python
# -*- coding: utf-8 -*-
from modules.logging import logging_decorator
from telegram.ext.dispatcher import run_async
from telegram.ext import CommandHandler
from telegram import ChatAction
import requests
import datetime


def module_init(gd):
    commands = gd.config["commands"]
    for command in commands:
        gd.dp.add_handler(CommandHandler(command, toristats, pass_args=True))


@logging_decorator("toribash")
def toristats(bot, update, args):
    update.message.chat.send_action(ChatAction.TYPING)
    user = args[0]
    toristats = "http://forum.toribash.com/tori_stats.php?format=json"
    full_link = toristats + "&username=" + user
    r = requests.get(full_link)
    try:
        tori_json = r.json()
    except:
        update.message.reply_text("No such player")
        return

    userid = tori_json["userid"]
    username = tori_json["username"]
    qi = tori_json["qi"]
    belt = tori_json["belt"]
    clanname = tori_json["clanname"]
    elo = tori_json["elo"]
    winratio = tori_json["winratio"]
    tc = tori_json["tc"]
    lastact = str(datetime.datetime.fromtimestamp(int(tori_json["lastactivity"])))

    output = ("User ID: " + userid + "\nUsername: " + username +
              "\nQi: " + str(qi) + ", " + belt +
              "\nClan: " + clanname +
              "\nWin Ratio: " + str(winratio)[:-2] + "%, " + str(elo)[:-4] + " elo" +
              "\nToricredits: " + str(tc)) + "\nLast Active: " + lastact
    update.message.reply_text(output)
    return user
