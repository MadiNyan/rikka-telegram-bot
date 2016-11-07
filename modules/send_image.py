#!/usr/bin/python
# -*- coding: utf-8 -*-


def send_image(bot, update, filepath, name, extension):
    photo_extensions = (".jpg", ".jpeg")
    doc_extensions = (".png", ".svg", ".tif", ".bmp", ".gif", ".mp4")
    sticker_extension = ".webp"
    for i in photo_extensions:
        if extension.endswith(i):
            with open(filepath + name + extension, "rb") as f:
                update.message.reply_photo(f)
            return True  
    for i in doc_extensions:
        if extension.endswith(i):
            with open(filepath + name + extension, "rb") as f:
                update.message.reply_document(f)
            return True
    if extension.endswith(sticker_extension):
        with open(filepath + name + extension, "rb") as f:
            update.message.reply_sticker(f)
        return True
