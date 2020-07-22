#!/usr/bin/python
# -*- coding: utf-8 -*-
from modules.logging import logging_decorator
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.patches import PathPatch
from telegram.ext import PrefixHandler
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
    commands = gd.config["commands"]
    for command in commands:
        gd.dp.add_handler(PrefixHandler("/", command, activity))
    conn = sqlite3.connect(db_path+"rikka.db", check_same_thread=False)
    c = conn.cursor()


@logging_decorator("activity")
def activity(update, context):
    names, amount, graph_title = usage_settings(update)
    plot(update, names, amount, graph_title)


def usage_settings(update):
    chat_id = update.message.chat.id
    if update.message.chat.title is not None:
        title_chat = update.message.chat.title
    else:
        title_chat = "this chat"
    c.execute("SELECT user, COUNT(*) FROM commands  WHERE chat_id = %s GROUP BY user" % (chat_id))
    r = c.fetchall()
    if r == []:
        update.message.reply_text("No commands used yet")
        return
    names, amount = get_values(r)
    graph_title = "Most active bot users in "+title_chat
    return names, amount, graph_title


def get_values(r):
    countsforsum = []
    for i in r:
        countsforsum.append(i[1])
    total = sum(countsforsum)
    below = []
    above = []
    for i in r: 
        if i[1] < total*0.05:
            below.append(i)
        else:
            above.append(i)
    otherstotal= []
    for i in below:
        otherstotal.append(i[1])
    others = sum(otherstotal)
    names, amount = map(list, zip(*above))    
    if others > 0:
        names.append("Others")
        amount.append(others)
    return names, amount


def plot(update, names, amount, graph_title):
    update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
    chat_id = update.message.chat.id
    _, ax = plt.subplots(figsize=(1000/my_dpi, 1000/my_dpi))
    plt.rcParams['savefig.facecolor']="#303030"
    pie, texts, autotexts = ax.pie(amount, radius=1.6, labels=names, autopct="%1.0f%%", pctdistance=0.8, labeldistance=1.05, shadow=False, colors=cs)
    for text in texts:
        text.set_color("#eeeeee")
    plt.setp(pie, edgecolor="#303030", linewidth=5, zorder=1)
    pie_logo = ax.pie(["1"], radius=1)
    plt.setp(pie_logo, zorder=-10)
    wedge = pie_logo[0][0]
    logo_path = os.path.abspath(graph_logo)
    image_file = cbook.get_sample_data(logo_path, asfileobj=False)
    image = plt.imread(image_file)
    wedge_path = wedge.get_path()
    patch = PathPatch(wedge_path)
    ax.add_patch(patch)
    imagebox = OffsetImage(image, zoom=0.73, interpolation="lanczos", clip_path=patch, zorder=-10)
    ab = AnnotationBbox(imagebox, (0, 0), xycoords="data", pad=0, frameon=False)
    ax.add_artist(ab)
    ax.axis("equal")
    plt.title(graph_title, color="#eeeeee")
    plt.tight_layout()
    graph_filename = path + str(chat_id) + "-graph.jpg"
    plt.savefig(graph_filename, format="jpg", bbox_inches="tight", pad_inches=0.2, dpi=my_dpi)
    with open(graph_filename, "rb") as f:
        update.message.reply_photo(f)
    os.remove(graph_filename)
