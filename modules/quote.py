#!/usr/bin/python
# -*- coding: utf-8 -*-
from modules.logging import logging_decorator
from telegram.ext.dispatcher import run_async
from telegram import ChatAction
from telegram.ext import MessageHandler, PrefixHandler
from modules.utils import Caption_Filter, send_image
from PIL import Image, ImageDraw, ImageOps
from wand.image import Image as wandImage
from wand.drawing import Drawing
from wand.color import Color
from wand.font import Font
from datetime import datetime
import random
import io
import os


def module_init(gd):
    global path, resources_path, font_path
    path = gd.config["path"]
    resources_path = gd.config["resources_path"]
    font_path = gd.config["font"]
    commands = gd.config["commands"]
    for command in commands:
        caption_filter = Caption_Filter("/"+command)
        gd.dp.add_handler(MessageHandler(caption_filter, quote))
        gd.dp.add_handler(PrefixHandler("/", commands, quote))


@run_async
@logging_decorator("quote")
def quote(update, context):
    filename = datetime.now().strftime("%d%m%y-%H%M%S%f")
    id, name, text = get_message(update, context)
    if text == "" or text == None:
        update.message.reply_text("Type in some text!")
        return
    update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
    profile_pic = get_profile_pic(context, filename, id, name)
    make_quote(profile_pic, filename, text, name)
    send_image(update, path, filename, ".jpg")
    os.remove(path+filename+".jpg")
    os.remove(path+filename+"pfp.jpg")


def make_quote(image, filename, text, author):
    background = Image.open(resources_path+"bg.jpg")
    avatar = Image.open(image)
    avatar_circle = circle(avatar)
    background.paste(avatar_circle, (50, 110), avatar_circle)
    watermark = Image.open(resources_path+"watermark.png").convert("RGBA")
    background.paste(watermark, (20, 540), watermark)
    binary_image = img_to_bytes(background, ".jpg")
    fit_text(binary_image, filename, text, author)


def get_message(update, context):
    reply = update.message.reply_to_message
    if reply is None:
        id = update.message.from_user.id
        name = update.message.from_user.full_name
        if update.message.caption is not None:
            text = update.message.caption[3:]
        else:
            text = " ".join(context.args)
    else:
        if reply.forward_from is None:
            id = reply.from_user.id
            name = reply.from_user.full_name
            if len(reply.photo) < 1:
                text = reply.text
            else:
                text = reply.caption
        else:
            id = reply.forward_from.id
            name = reply.forward_from.full_name
            if len(reply.photo) < 1:
                text = reply.text
            else:
                text = reply.caption
    return id, name, text


def get_profile_pic(context, filename, id, name):
    pfp_path = path+filename+"pfp.jpg"
    if len(context.bot.getUserProfilePhotos(id, limit = 1).photos) == 0:
        generate_profile_pic(pfp_path, name)
    else:
        pfp = context.bot.getUserProfilePhotos(id, limit = 1).photos[0][-1].file_id
        context.bot.getFile(pfp).download(pfp_path)
    return pfp_path


def generate_profile_pic(save_path, name):
    words = name.split()
    letters = [word[0] for word in words]
    initials = "".join(letters)
    colors =["#c75650", "#d67a27", "#7e6ccf", "#4eb331", "#2ea4ca"]
    with wandImage(width = 756, height = 756, background = Color(random.choice(colors))) as img:
        left, top, width, height = 200, 265, 340, 240
        with Drawing() as context:
            font = Font(font_path, color="white")
            context(img)
            img.caption(initials, left=left, top=top, width=width, height=height, font=font, gravity="center")
            img.save(filename=save_path)
    return save_path


def circle(image):
    mask = Image.open(resources_path+"mask.png").convert("L")
    circle = ImageOps.fit(image, mask.size, centering=(0.5, 0.5))
    circle.putalpha(mask)
    stroke = Image.new("RGBA", (756,756), (255,255,255,0))
    draw = ImageDraw.Draw(stroke)
    draw.ellipse((0, 0, 755, 755), width=18, outline ="white")
    stroke = stroke.resize((378, 378), resample=Image.ANTIALIAS)
    circle.paste(stroke, (0,0), stroke)
    return circle


def img_to_bytes(file, ext):
	fp = io.BytesIO()
	format = Image.registered_extensions()[ext]
	file.save(fp, format)
	return fp.getvalue()


def fit_text(img, filename, text, name):
    text = "«" + text + "»"
    name = "—  " + name
    with wandImage(blob=img) as canvas:
        text_left, text_top, text_width, text_height = 475, 50, 675, 410
        name_left, name_top, name_width, name_height = 530, 460, 570, 50
        with Drawing() as context:
            font = Font(font_path, color="white")
            context(canvas)
            canvas.caption(text, left=text_left, top=text_top, width=text_width, height=text_height, font=font, gravity="center")
            canvas.caption(name, left=name_left, top=name_top, width=name_width, height=name_height, font=font, gravity="center")
            canvas.save(filename=path+filename+".jpg")
