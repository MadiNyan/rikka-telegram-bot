#!/usr/bin/python
# -*- coding: utf-8 -*-
from modules.utils import caption_filter, get_image_new, send_image_new
from modules.logging import logging_decorator
from telegram.ext import CommandHandler, MessageHandler
from telegram import ChatAction
from wand.image import Image
import io


def module_init(gd):
    global img_mimetypes
    img_mimetypes = gd.config["types"]
    commands = gd.config["commands"]
    for command in commands:
        gd.dp.add_handler(MessageHandler(caption_filter("/"+command), kek))
        gd.dp.add_handler(CommandHandler(command, kek))


@logging_decorator("kek")
def kek(bot, update):
    if update.message.reply_to_message is not None:
        kek_param = "".join(update.message.text[5:7])
    elif update.message.caption is not None:
        kek_param = "".join(update.message.caption[5:7])
    else:
        update.message.reply_text("You need an image for that!")
        return
    try:
        myfile, img_mimetype = get_image_new(bot, update)
    except:
        update.message.reply_text("Can't get the image")
        return
    if img_mimetype not in img_mimetypes:
        update.message.reply_text("Unsupported file")
        return False
    else:
        blob_format = img_mimetypes[img_mimetype]
    update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
    w, h, result = kekify(kek_param, myfile)
    result = result.make_blob(blob_format)
    result = io.BytesIO(result)
    send_image_new(update, result, img_mimetype)
    result.close()


def kekify(kek_param, myfile):
    if kek_param == "-m":
        result = multikek(myfile)
        return None, None, result
    with Image(blob=myfile) as source:
        w = source.width; h = source.height
        c, p1, p2, f = get_values(kek_param, w, h)
        with source.clone() as part1:
            part1.crop(c[0], c[1], c[2], c[3])
            with part1.clone() as part2:    
                getattr(part2, f)()
                new_canvas = Image()
                new_canvas.blank(w, h)
                new_canvas.composite(part1, p1[0], p1[1])
                new_canvas.composite(part2, p2[0], p2[1])
    return w, h, new_canvas


def multikek(image):
    w, h, canvasL = kekify("-l", image)
    w, h, canvasR = kekify("-r", image)
    w, h, canvasT = kekify("-t", image)
    w, h, canvasB = kekify("-b", image)
    big_canvas = Image()
    big_canvas.blank(w*2, h*2)
    big_canvas.composite(canvasL, 0, 0)
    big_canvas.composite(canvasR, w, 0)
    big_canvas.composite(canvasT, 0, h)
    big_canvas.composite(canvasB, w, h)
    canvasL.close()
    canvasR.close()
    canvasT.close()
    canvasB.close()
    return big_canvas


def get_values(kek_param, w, h):
    parameters = {
        "":   [[0, 0, w//2, h], [0, 0], [w//2, 0], "flop"],
        "-l": [[0, 0, w//2, h], [0, 0], [w//2, 0], "flop"],
        "-r": [[w//2, 0, w, h], [w//2, 0], [0, 0], "flop"],
        "-t": [[0, 0, w, h//2], [0, 0], [0, h//2], "flip"],
        "-b": [[0, h//2, w, h], [0, h//2], [0, 0], "flip"],
        }
    try:
        params = parameters[kek_param]
    except KeyError:
        params = parameters[""]
    return params
