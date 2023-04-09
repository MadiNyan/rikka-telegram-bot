import json
import re
from random import randint
from urllib.parse import quote_plus

import requests
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import PrefixHandler

from modules.logging import logging_decorator


def module_init(gd):
    commands_image = gd.config["commands_image"]
    commands_gif = gd.config["commands_gif"]
    for command in commands_image:
        gd.application.add_handler(PrefixHandler("/", command, image_search))
    for command in commands_gif:
        gd.application.add_handler(PrefixHandler("/", command, gif_search))


@logging_decorator("img")
async def image_search(update: Update, context):
    query = await google_search(update, context)
    return query


@logging_decorator("gif")
async def gif_search(update: Update, context):
    query = await google_search(update, context, gif=True)
    return query
    

async def google_search(update, context, gif=False):
    query = quote_plus(" ".join(context.args))
    if len(query) == 0:
        await update.message.reply_text("You need a query to search!")
        return
    await update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
    try:
        final_img = single_result(get_image(query, gif))
    except Exception as e:
        print(e)
        await update.message.reply_text("Sorry, something gone wrong!")
        return
    if final_img is None:
        await update.message.reply_text("Nothing found!")
        return
    msg_text = "[link](%s)" % final_img
    await update.message.reply_text(msg_text, parse_mode="Markdown", disable_web_page_preview=False)


def get_image(query, gif=False):
    if gif:
        link = "https://www.google.ru/search?q={}&tbm=isch&tbs=itp%3Aanimated".format(query)
    else:
        link = "https://www.google.ru/search?q={}&tbm=isch".format(query)
    req = requests.get(link, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.142 Safari/537.36",
            "cookie": "NID=78=NU42mV7XN8ISKCdBMB0fl93m5CFCt7iXvqbNUZul1SJX01yYIYR-MFdGan1sJ59OMY75QZQqjyn3i88jHH-qLX9VQ72p6Dp6z28Fh1BrR4cfgMPLxSuEULn3Yj3-f9-Tw0Zsn0708me2wiixK0YW5MG5rLQj5JpydcJjH9zXIJzMpg"
            })
    html_output = req.text
    googleregex = r"/AF_initDataCallback\({key: 'ds:1', hash: '5', data:(.*), sideChannel: {}}\);<\/script><script/gmis"
    html_links = re.search(googleregex, html_output, re.M | re.I | re.S).group(1)
    full_json = json.loads(html_links)
    found_arr = None

    for item1lvl in full_json:
        if not isinstance(item1lvl, list):
            continue
        for item2lvl in item1lvl:
            if not isinstance(item2lvl, list):
                continue
            for item3lvl in item2lvl:
                if item3lvl and item3lvl[0] == "GRID_STATE0":
                    found_arr = item3lvl
                    break

    print("found:", found_arr)

    image_arr = found_arr[2]

    images = [x[1][3][0] for x in image_arr if x[1] and x[1][3] and x[1][3][0] and x[1][3][0].startswith("http")]

    return images


def single_result(links_list):
    if len(links_list) < 1:
        return None
    else:
        return links_list[randint(0, len(links_list)-1)]
