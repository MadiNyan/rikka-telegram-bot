#!/usr/bin/python
# -*- coding: utf-8 -*-
# Module courtesy of Slko
import requests
import subprocess
import os.path


def extract_url(entity, text):
    if entity["type"] == "text_link":
        return entity["url"]
    elif entity["type"] == "url":
        offset = entity["offset"]
        length = entity["length"]
        return text[offset:offset+length]
    else:
        return None


def is_image(path):
    image_extensions = (".jpg", ".jpeg", ".png", ".gif", ".svg", ".tif", ".bmp", ".mp4")
    if path is None:
        return False
    for i in image_extensions:
        if path.casefold().endswith(i):
            ext = i
            return ext
    return False


def get_image(bot, update, dl_path):
    output = os.path.join(dl_path, "original")
    reply = update.message.reply_to_message
    if reply is None:
        extension = ".jpg"
        bot.getFile(update.message.photo[-1].file_id).download(output + extension)
        return extension
    # Entities; url, text_link
    if reply.entities is not None:
        urls = (extract_url(x, reply.text) for x in reply.entities)
        images = [x for x in urls if is_image(x)]
        if len(images) > 0:
            extension = is_image(images[0])
            r = requests.get(images[0])  # use only first image url
            with open(output+extension, "wb") as f:
                f.write(r.content)
            return extension
    # Document
    if reply.document is not None and is_image(reply.document.file_name):
        extension = is_image(reply.document.file_name)
        bot.getFile(reply.document.file_id).download(output + extension)
        return extension
    # Sticker
    if reply.sticker is not None:
        extension = ".webp"
        bot.getFile(reply.sticker.file_id).download(output+extension)
        return extension
    # Photo in reply
    if reply.photo is not None:
        extension = ".jpg"
        bot.getFile(reply.photo[-1].file_id).download(output + extension)
        return extension
    return False
