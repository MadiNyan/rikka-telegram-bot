#!/usr/bin/python
# -*- coding: utf-8 -*-
from modules.utils import Caption_Filter, get_param, get_image, send_image, mp4_fix
from modules.logging import logging_decorator
from telegram.ext import PrefixHandler, MessageHandler
from telegram.ext.dispatcher import run_async
from telegram import ChatAction
from datetime import datetime
from wand.image import Image
from itertools import chain
import os

coords_by_frame = (
[(58, 28), (164, 24), (168, 106), (63, 114)],
[(59, 28), (165, 24), (169, 106), (64, 114)],
[(60, 28), (166, 24), (170, 106), (65, 114)],
[(60, 28), (166, 24), (170, 106), (65, 114)],
[(60, 27), (166, 23), (170, 105), (65, 113)],
[(61, 26), (167, 22), (171, 104), (66, 112)],
[(59, 25), (163, 21), (171, 100), (67, 107)],
[(57, 26), (155, 23), (171, 93), (68, 99)],
[(57, 26), (154, 26), (169, 87), (66, 88)],
[(55, 30), (149, 33), (165, 78), (67, 73)],
[(49, 40), (144, 52), (168, 76), (66, 63)],
[(57, 51), (143, 66), (162, 76), (67, 58)],
[(63, 51), (138, 67), (163, 75), (72, 55)],
[(63, 40), (150, 58), (168, 72), (68, 51)],
[(59, 36), (152, 54), (170, 73), (69, 52)],
[(57, 43), (148, 51), (170, 75), (72, 66)],
[(48, 47), (141, 59), (166, 83), (68, 69)],
[(37, 46), (133, 49), (140, 82), (36, 77)],
[(40, 40), (133, 50), (137, 79), (32, 65)],
[(43, 36), (137, 45), (144, 74), (40, 62)],
[(46, 32), (139, 42), (150, 70), (47, 58)],
[(45, 32), (141, 40), (157, 70), (51, 59)],
[(43, 32), (137, 41), (154, 71), (48, 58)]
)


def module_init(gd):
    global path, launchpad_gif
    path = gd.config["path"]
    launchpad_gif = gd.config["launchpad_path"]
    commands = gd.config["commands"]
    for command in commands:
        caption_filter = Caption_Filter("/"+command)
        gd.dp.add_handler(MessageHandler(caption_filter, fap))
        gd.dp.add_handler(PrefixHandler("/", command, fap))


@run_async
@logging_decorator("fap")
def fap(update, context):
    filename = datetime.now().strftime("%d%m%y-%H%M%S%f")
    try:
        extension = get_image(update, context, path, filename)
    except:
        update.message.reply_text("I can't get the image! :(")
        return
    update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)

    with Image(filename=path+filename+extension) as decal:
        decal.resize(320, 172)
        w, h = decal.size
        decal.virtual_pixel = 'transparent'
        source_points = (
            (0, 0),
            (w, 0),
            (w, h),
            (0, h)
        )
        with Image(filename=launchpad_gif) as template_gif:
            new = Image()
            for i in range(len(template_gif.sequence)):
                with template_gif.sequence[i] as frame: 
                    img = Image(image=frame)
                    img.delay = 6
                destination_points = (coords_by_frame[i])
                order = chain.from_iterable(zip(source_points, destination_points))
                arguments = list(chain.from_iterable(order))
                decal_current = Image(image=decal)
                decal_current.matte_color = "rgba(255, 255, 255, 0)"
                decal_current.distort('perspective', arguments)
                img.composite(decal_current,left=0,top=0)
                new.sequence.append(img)
                decal_current.close()
                img.close()
            new.save(filename=path+"result.mp4")
            result_filename = mp4_fix(path, "result")
            send_image(update, path, result_filename, ".mp4")
            new.close()
            os.remove(path+result_filename+".mp4")
            os.remove(path+filename+extension)
