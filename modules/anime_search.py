import random
import io
import aiohttp
import mimetypes
import urllib.parse

from typing import Tuple
from aiohttp_socks import ProxyConnector
from telegram import Update
from telegram.ext import PrefixHandler

from modules.logging import logging_decorator
from modules.utils import send_image, send_chat_action

gelbooru_request_link = "https://gelbooru.com/index.php"
gelbooru_post_link = "https://gelbooru.com/index.php?page=post&s=view&id="


def module_init(gd):
    global proxy_url, base_query, custom_query
    commands = gd.config["commands"]
    proxy_server = gd.config["proxy"]["server"]
    if gd.config["proxy"]["enabled"] is True:
        proxy_url = f"socks5://{proxy_server}"
    else:
        proxy_url = None
    base_query = gd.config["base_query"]
    custom_query = gd.config["custom_query"]
    
    gd.application.add_handler(PrefixHandler("/", commands, gelbooru_search))


@logging_decorator("gelbooru")
async def gelbooru_search(update: Update, context):
    query = await search(update, context, gelbooru_request_link, gelbooru_post_link)
    return query


async def search(update, context, request_link, post_link):
    if update.message is None: return
    
    if context.args:
        query = " ".join(context.args) + " " + custom_query
    else:
        query = base_query

    try:
        direct_link, post_id, sample_link, spoiler = await get_gelbooru_image(query, request_link, proxy_url)
    except Exception as e:
        await update.message.reply_text(f"Error retrieving image:\n{str(e)}")
        return query
    if direct_link == "":
        await update.message.reply_text("Nothing found!")
        return query
    image_bytes = await gelbooru_download_image(direct_link, proxy_url)
    if image_bytes is None:
        await update.message.reply_text("Could not download image")
        return query
    
    
    page_link = post_link + post_id
    msg_text = "[View post]({})".format(page_link)
    caption = (msg_text, "Markdown")
    attachment_type, mime_type = await check_attachment_type(direct_link)
    if attachment_type == "photo" and image_bytes.getbuffer().nbytes > 10000000:
        attachment_type = "document"
    await send_chat_action(update, context, attachment_type)
    try:
        await send_image(update, image_bytes, mime_type, attachment_type, None, caption=caption, has_spoiler=bool(spoiler))
    except Exception("BadRequest") as e:
        print(e)
    return query


async def get_gelbooru_image(query, request_link, proxy_url) -> Tuple[str, str, str, bool]:
    # Query parameters for Gelbooru API
    params = {
        "tags": query,
        "json": 1,
        "page": "dapi",
        "s": "post",
        "q": "index"
    }
    
    # Use urlencode but preserve certain characters
    params_str = urllib.parse.urlencode(params, safe=":>+ ")  # Added space and > to safe chars
    
    connector = ProxyConnector.from_url(proxy_url, rdns=False) if proxy_url else None
    async with aiohttp.ClientSession(connector=connector) as session:
        async with session.get(request_link, params=params_str) as response:
            result_obj = await response.json()
    
    if not response.text:
        return "", "", "", False
    if not result_obj:
        return "", "", "", False
    if result_obj["@attributes"]["count"] == 0:  # check if nothing found
        return "", "", "", False
    
    post = random.choice(result_obj["post"])
    direct_link, post_id, sample_link, post_rating = post.get("file_url"), str(post.get("id")), post.get("sample_url"), post.get("rating")
    if post_rating.lower() == "questionable" or post_rating.lower() == "sensitive" or post_rating.lower() == "explicit":
        spoiler = True
    else:
        spoiler = False
    sample_link = direct_link if sample_link is None else sample_link
    return direct_link, post_id, sample_link, spoiler


async def gelbooru_download_image(image_url, proxy_url):
    connector = ProxyConnector.from_url(proxy_url, rdns=False) if proxy_url else None
    async with aiohttp.ClientSession(connector=connector) as session:
        async with session.get(image_url) as response:
            if response.status == 200:
                return io.BytesIO(await response.read())
            return None


async def check_attachment_type(direct_link):
    mime_type = mimetypes.guess_type(direct_link)[0]
    if mime_type is None:
        return "document", "application/octet-stream"
    if mime_type.startswith("video"):
        return "video", mime_type
    elif mime_type.startswith("image/gif"):
        return "animation", mime_type
    elif mime_type.startswith("image"):
        return "photo", mime_type
    else:
        return "document", mime_type
