import json
import os
import random
from datetime import datetime

import requests
import yaml
from PIL import Image, ImageChops, ImageOps
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import MessageHandler, PrefixHandler, filters

from modules.logging import logging_decorator
from modules.utils import get_image, get_param

bleed = 100


def module_init(gd):
    global path, resources_path, templates_dict, templates_path, token, extensions
    path = gd.config["path"]
    extensions = gd.config["extensions"]
    resources_path = gd.config["resources_path"]
    templates_path = resources_path+"templates/"
    token = gd.full_config["keys"]["telegram_token"]
    commands = gd.config["commands"]
    for command in commands:
        gd.application.add_handler(MessageHandler(filters.PHOTO & filters.CaptionRegex(r'/'+command+''), merch))
        gd.application.add_handler(PrefixHandler("/", command, merch))
    with open(resources_path+"templates.yml", "r") as f:
        templates_dict = yaml.load(f, Loader=yaml.SafeLoader)


@logging_decorator("merch")
async def merch(update: Update, context):
    if update.message is None: return
    filename = datetime.now().strftime("%d%m%y-%H%M%S%f")
    try:
        extension = await get_image(update, context, path, filename)
    except:
        await update.message.reply_text("I can't get the image! :(")
        return
    if extension not in extensions:
        await update.message.reply_text("Unsupported file")
        return False
    await update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
    templates_list = list(templates_dict.keys())

    if len(context.args)>0:
        if context.args[0] in templates_list:
            amount = 1
            template = True
        else:
            amount = await get_param(update, 1, 1, 10)
            template = False
    else:
        amount = await get_param(update, 1, 1, 10)
        template = False
 
    image = path+filename+extension
    photos = []
    upload_files = []
    for i in range(amount):
        if template is True:
            product = context.args[0]
        else:
            product = random.choice(templates_list)
        templates_list.remove(product)
        result_image = make_merch(image, templates_path, templates_dict[product], templates_dict[product]["offset"])
        result_image.save(path+"merch"+str(i)+".jpg")
        
        image_to_attach = "merch"+str(i)+".jpg"
        attach_name = "".join(random.choice("abcdef1234567890") for x in range(16))
        photos.append({"type": "photo", "media": "attach://" + attach_name})
        upload_files.append((attach_name, (image_to_attach, open(path+image_to_attach, "rb"))))
        
    requests.post("https://api.telegram.org/bot"+token+"/sendMediaGroup", params={"chat_id": update.message.chat.id, "media": json.dumps(photos)}, files=upload_files, timeout=120)
    os.remove(path+filename+extension)
    return amount


def make_merch(image_to_print, templates_path, template, offset=(0,0)):
    source = Image.open(templates_path + template["img"])
    source = source.convert("RGBA")
    width, height = source.size
    long_side = max(source.size)

    mask = Image.open(templates_path + template["mask"])
    mask = mask.convert("RGBA")

    decal = Image.open(image_to_print)
    decal = ImageOps.fit(decal, mask.size, Image.LANCZOS)
    decal = decal.convert("RGBA")

    bg = Image.open(resources_path+"background.jpg")
    bg = ImageOps.fit(bg, (long_side+bleed, long_side+bleed), Image.LANCZOS)

    cutout = ImageChops.multiply(decal, mask)

    transparent_canvas = Image.new('RGBA', bg.size, color=(0, 0, 0, 0))
    transparent_canvas.paste(cutout, offset, cutout)
    offset_decal = transparent_canvas

    displaced = ImageChops.multiply(offset_decal, source)
    product = ImageChops.composite(displaced, source, displaced)
    bg.paste(product, ((bg.width-width)//2, (bg.height-height)//2), product)
    
    watermark = Image.open(resources_path+"watermark.png").convert("RGBA")
    bg.paste(watermark, (20, bg.height-watermark.height-20), watermark)

    final = bg.convert("RGB")
    return final
