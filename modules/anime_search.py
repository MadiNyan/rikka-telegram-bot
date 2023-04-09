import random
import urllib.parse

import aiohttp
from aiohttp_socks import ProxyConnector
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import PrefixHandler

from modules.logging import logging_decorator

yandere_request_link = "https://yande.re/post.json?limit=100"
yandere_post_link = "https://yande.re/post/show/"
gelbooru_request_link = "https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1"
gelbooru_post_link = "https://gelbooru.com/index.php?page=post&s=view&id="




def module_init(gd):
    global proxyuser, proxypassword, proxyserver
    commands_gelbooru = gd.config["commands_gelbooru"]
    commands_yandere = gd.config["commands_yandere"]
    proxyuser = gd.config["proxy"]["user"]
    proxypassword = gd.config["proxy"]["password"]
    proxyserver = gd.config["proxy"]["server"]
    for command in commands_gelbooru:
        gd.application.add_handler(PrefixHandler("/", command, gelbooru_search))
    for command in commands_yandere:
        gd.application.add_handler(PrefixHandler("/", command, yandere_search))


@logging_decorator("yandere")
async def yandere_search(update: Update, context):
    query = await search(update, context, yandere_request_link, yandere_post_link)
    return query


@logging_decorator("gelbooru")
async def gelbooru_search(update: Update, context):
    query = await search(update, context, gelbooru_request_link, gelbooru_post_link, "gelbooru")
    return query


async def search(update, context, request_link, image_link, search_place="yandere"):
    if update.message is None: return
    await update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
    query = " ".join(context.args) if context.args else ""
    try:
        if search_place == "gelbooru":
            direct_link, page_link, sample_link = await get_gelbooru_image(query, request_link, image_link)
        else:
            direct_link, page_link, sample_link = await get_image(query, request_link, image_link)
            
    except Exception as e:
        print(e)
        await update.message.reply_text("Sorry, something went wrong!")
        return query
    if direct_link is None:
        await update.message.reply_text("Nothing found!")
        return query
    msg_text = "[Image]({})".format(direct_link) + "\n" + "[View post]({})".format(page_link)
    await update.message.reply_text(msg_text, parse_mode="Markdown")
    return query


async def get_gelbooru_image(query, request_link, image_link):
    params = {"tags": query.replace(" ", "+")}  # replace space for plus symbol
    params_str = urllib.parse.urlencode(params, safe=":+")  # prevent percenting symbols in request
    connector = ProxyConnector.from_url("socks5://"+proxyuser+":"+proxypassword+"@"+proxyserver, rdns=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        async with session.get(request_link, params=params_str) as response:
            result_obj = await response.json()
    if not response.text:
        return None, None, None
    if not result_obj:
        return None, None, None
    if result_obj["@attributes"]["count"] == 0:  # check if nothing found
        return None, None, None
    post = random.choice(result_obj["post"])  # get random post from list
    direct_link, page_link, sample_link = post.get("file_url"), image_link+str(post.get("id")), post.get("sample_url")
    return direct_link, page_link, sample_link


async def get_image(query, request_link, image_link):
    params = {"tags": query}
    connector = ProxyConnector.from_url("socks5://"+proxyuser+":"+proxypassword+"@"+proxyserver, rdns=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        async with session.get(request_link, params=params) as response:
            result_list = await response.json()
    if not response.text:
        return None, None, None
    if not result_list:
        return None, None, None
    post = random.choice(result_list)
    direct_link, page_link, sample_link = post.get("file_url"), image_link+str(post.get("id")), post.get("sample_url")
    return direct_link, page_link, sample_link
