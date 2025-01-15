import io
import random

from datetime import datetime
from telegram import Update
from telegram.ext import PrefixHandler

from modules.anime_search import get_gelbooru_image, check_attachment_type, gelbooru_download_image
from modules.logging import logging_decorator
from modules.meme import fonts_dict, text_format, make_meme
from modules.nya import files, path
from modules.utils import send_image, send_chat_action


gelbooru_request_link = "https://gelbooru.com/index.php"


def module_init(gd):
    global proxy_url, query
    commands_nyameme = gd.config["commands_nyameme"]
    commands_animeme = gd.config["commands_animeme"]
    proxy_server = gd.config["proxy"]["server"]
    query = gd.config["query"]
    if gd.config["proxy"]["enabled"] is True:
        proxy_url = f"socks5://{proxy_server}"
    else:
        proxy_url = None
    
    gd.application.add_handler(PrefixHandler("/", commands_nyameme, nyameme))
    gd.application.add_handler(PrefixHandler("/", commands_animeme, animeme))


@logging_decorator("nyameme")
async def nyameme(update: Update, context):
    if update.message is None: return
    font, args = await get_font(context.args)
    meme_text = await get_text(update, args)
    if meme_text is None:
        return
    top_text, bottom_text = await text_split(meme_text)
    random_image = random.choice(files)
    clean_image = io.BytesIO(open(path+random_image, "rb").read())
    await send_chat_action(update, context, "photo")
    memed_image = await make_meme(top_text, bottom_text, clean_image, font)
    await send_image(update, memed_image, "image/jpeg", "photo", None, has_spoiler=False)
    return


@logging_decorator("animeme")
async def animeme(update: Update, context):
    if update.message is None: return
    await send_chat_action(update, context, "photo")
    font, args = await get_font(context.args)
    meme_text = await get_text(update, args)
    if meme_text is None:
        return
    top_text, bottom_text = await text_split(meme_text)
    image_query = query
    
    try:
        # Get random anime image
        direct_link, _, sample_link, spoiler = await get_gelbooru_image(image_query, gelbooru_request_link, proxy_url)
        if not sample_link:
            await update.message.reply_text("Failed to get image")
            return
            
        attachment_type, mime_type = await check_attachment_type(direct_link)
        if attachment_type != "photo":
            await update.message.reply_text("Unexpected file type")
            return

        # Download image
        clean_image = await gelbooru_download_image(sample_link, proxy_url)
        memed_image = io.BytesIO()
            
        await send_chat_action(update, context, "photo")
        memed_image = await make_meme(top_text, bottom_text, clean_image, font)
        filename = datetime.now().strftime("%d%m%y-%H%M%S%f")
        await send_image(update, memed_image, mime_type, "photo", filename, has_spoiler=spoiler)
        
    except Exception as e:
        await update.message.reply_text(f"Error during processing:\n{str(e)}")
        return


async def get_text(update, args):
    # Get text from reply
    reply = update.message.reply_to_message
    if reply:
        if reply.caption:
            args = reply.caption
        elif reply.text:
            args = reply.text
        else:
            args = " ".join(args)
        args = args.split(" ")
    else:
        pass
    if len(args) < 1:
        await update.message.reply_text("Type in some text!")
        return None
    return args


async def text_split(text_list):
    # Split text into top and bottom text
    if text_list == None:
        return "", ""
    if len(text_list) == 1:
        top_text = None
        bottom_text = text_list[0]
    elif "@" in text_list:
        split_text = " ".join(text_list)
        top_text, bottom_text = text_format(split_text)
    else:
        split_spot = random.randint(1, len(text_list)-1)
        top_text = " ".join(text_list[:split_spot])
        bottom_text = " ".join(text_list[split_spot:])
    return top_text, bottom_text


async def get_font(args):
    rand_font = random.choice(list(fonts_dict))
    font = fonts_dict[rand_font]
    if len(args) < 1:
        return font, args
    else:
        for i in fonts_dict:
            if "-"+i in args[0] or "-"+i[0] in args[0]:
                font = fonts_dict[i]
                args = args[1:]
                break
    return font, args