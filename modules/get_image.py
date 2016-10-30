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
        offset = entity[i]["offset"]
        length = entity[i]["length"]
        return text[offset:offset+length]
    else:
        return None


def is_image(path):
    image_extensions = (".jpg", ".png", ".gif")
    if path is None:
        return False
    return path.casefold().endswith(image_extensions)


def get_image(bot, update, dl_path):
    output = os.path.join(dl_path, "original.jpg")
    temp_png = os.path.join(dl_path, "original.png")
    reply = update.message.reply_to_message
    if reply is None:
        return False
    # Entities; url, text_link
    if reply.entities is not None:
        urls = (extract_url(x, reply.text) for x in reply.entities)
        images = [x for x in urls if is_image(x)]
        if len(images) > 0:
            r = requests.get(images[0])  # use only first image url
            with open(output, "wb") as f:
                f.write(r.content)
            return True
    # Document
    if reply.document is not None and is_image(reply.document.file_name):
        bot.getFile(reply.document.file_id).download(output)
        return True
    # Sticker
    if reply.sticker is not None:
        bot.getFile(reply.sticker.file_id).download(output)
        stick = "convert  " + temp_png + " -background white -flatten " + output
        subprocess.run(stick, shell=True)
        return True
    # Photo in reply
    if reply.photo is not None:
        bot.getFile(reply.photo[-1].file_id).download(output)
        return True
    return False
