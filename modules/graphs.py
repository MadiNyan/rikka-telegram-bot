#!/usr/bin/python
# -*- coding: utf-8 -*-
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.patches import PathPatch
from telegram.ext import CommandHandler
import matplotlib.cbook as cbook
from telegram import ChatAction
import matplotlib.pyplot as plt
from datetime import datetime
from matplotlib import style
import sqlite3
import os

style.use("fivethirtyeight")
cs = ["#1f77b4", "#aec7e8", "#ff7f0e", "#ffbb78", "#2ca02c",
      "#98df8a", "#d62728", "#ff9896", "#9467bd", "#c5b0d5",
      "#8c564b", "#c49c94", "#e377c2", "#f7b6d2", "#7f7f7f",
      "#c7c7c7", "#bcbd22", "#dbdb8d", "#17becf", "#9edae5"]
my_dpi = 100


def module_init(gd):
    global c, conn, path, graph_logo
    path = gd.config["path"]
    db_path = gd.config["db_path"]
    graph_logo = gd.config["graph_logo"]
    commands_activity = gd.config["commands_activity"]
    commands_usage = gd.config["commands_usage"]
    for command in commands_activity:
        gd.dp.add_handler(CommandHandler(command, activity, pass_args=True))
    for command in commands_usage:
        gd.dp.add_handler(CommandHandler(command, usage, pass_args=True))
    conn = sqlite3.connect(db_path+"rikka.db", check_same_thread=False)
    c = conn.cursor()


def usage(bot, update, args):
    func_name = "usage"
    current_time = datetime.strftime(datetime.now(), "%d.%m.%Y %H:%M:%S")
    if "all" in "".join(args):
        chat_mode = "all"
    else:
        chat_mode = "local"
    labels, counts, graph_title = usage_settings(chat_mode, update, func_name)
    plot(update, labels, counts, graph_title)
    print(current_time, ">", "/usage", ">", update.message.from_user.username)


def activity(bot, update, args):
    func_name = "activity"
    current_time = datetime.strftime(datetime.now(), "%d.%m.%Y %H:%M:%S")
    chat_mode = "local"
    labels, counts, graph_title = usage_settings(chat_mode, update, func_name)
    plot(update, labels, counts, graph_title)
    print(current_time, ">", "/activity", ">", update.message.from_user.username)


def usage_settings(chat_mode, update, func_name):
    chat_id = update.message.chat.id
    if update.message.chat.title is not None:
        chat_title = update.message.chat.title
    else:
        chat_title = "this chat"
    if func_name is "usage":
        title_mode = "used commands"
        if chat_mode == "local":
            c.execute("SELECT command, COUNT(*) FROM commands WHERE chat_id = %s GROUP BY command" % (chat_id))
            title_chat = chat_title
        elif chat_mode == "all":
            c.execute("SELECT command, COUNT(*) FROM commands GROUP BY command")
            title_chat = "all chats"
    elif func_name is "activity":
        title_mode = "active bot users"
        c.execute("SELECT user, COUNT(*) FROM commands  WHERE chat_id = %s GROUP BY user" % (chat_id))
        title_chat = chat_title
    r = c.fetchall()
    items = []
    counts = []
    for i in r:
        items.append(i[0])
        counts.append(i[1])
    graph_title = "Most "+title_mode+" in "+title_chat
    return items, counts, graph_title


def plot(update, labels, counts, graph_title):
    update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
    chat_id = update.message.chat.id
    _, ax = plt.subplots(figsize=(1000/my_dpi, 1000/my_dpi))
    pie, _, _ = ax.pie(counts, radius=1.6, labels=labels, autopct="%1.0f%%", pctdistance=0.8, labeldistance=1.05, shadow=False, colors=cs)
    plt.setp(pie, edgecolor='w', zorder=1)
    pie_logo = ax.pie(["1"], radius=1)
    plt.setp(pie_logo, zorder=-10)
    wedge = pie_logo[0][0]
    logo_path = os.path.abspath(graph_logo)
    image_file = cbook.get_sample_data(logo_path, asfileobj=False)
    image = plt.imread(image_file)
    wedge_path = wedge.get_path()
    patch = PathPatch(wedge_path, facecolor="w")
    ax.add_patch(patch)
    imagebox = OffsetImage(image, zoom=0.73, interpolation="lanczos", clip_path=patch, zorder=-10)
    ab = AnnotationBbox(imagebox, (0, 0), xycoords="data", pad=0, frameon=False)
    ax.add_artist(ab)
    ax.axis("equal")
    plt.title(graph_title)
    plt.tight_layout()
    graph_filename = path + str(chat_id) + "-graph.png"
    plt.savefig(graph_filename, format="png", bbox_inches="tight", pad_inches=0.2, dpi=my_dpi, facecolor="w")
    with open(graph_filename, "rb") as f:
        update.message.reply_photo(f)
