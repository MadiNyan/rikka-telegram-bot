import os
from datetime import datetime

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import MessageHandler, PrefixHandler
from wand.image import Image

from modules.logging import logging_decorator
from modules.utils import Caption_Filter, get_image, mp4_fix, send_image


def module_init(gd):
    global path, extensions
    extensions = gd.config["extensions"]
    commands = gd.config["commands"]
    path = gd.config["path"]
    for command in commands:
        # caption_filter = Caption_Filter("/"+command)
        # gd.application.add_handler(MessageHandler(caption_filter, kek))
        gd.application.add_handler(PrefixHandler("/", command, kek))


@logging_decorator("kek")
async def kek(update: Update, context):
    if update.message is None: return
    filename = datetime.now().strftime("%d%m%y-%H%M%S%f")
    if update.message.reply_to_message is not None:
        kek_param = "".join(update.message.text[5:7])
    elif update.message.caption is not None:
        kek_param = "".join(update.message.caption[5:7])
    else:
        await update.message.reply_text("You need an image for that")
        return
    try:
        extension = await get_image(update, context, path, filename)
    except:
        await update.message.reply_text("Can't get the image")
        return
    if extension not in extensions:
        await update.message.reply_text("Unsupported file")
        return False
    await update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
    
    if extension in [".mp4", ".gif"]:
        if kek_param == "-m":
            await update.message.reply_text("Multikek unsupported for animations")
            return
        result = kekify_gifs(kek_param, filename, extension)
    else:
        _, _, result = kekify(kek_param, filename, extension, None)
    result.save(filename=path+filename+extension)
    result.close()
    if extension == ".mp4":
        filename = mp4_fix(path, filename)
    await send_image(update, path, filename, extension)
    os.remove(path+filename+extension)


def kekify(kek_param, filename, extension, file):
    if kek_param == "-m":
        result = multikek(filename, extension)
        return None, None, result
    if file == None:
        source = Image(filename=path+filename+extension)
    else:
        source = file
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
    source.close()
    return w, h, new_canvas
    
def kekify_gifs(kek_param, filename, extension):
    with Image(filename=path+filename+extension) as source:
        w = source.width; h = source.height
        new = Image()
        for frame in source.sequence:
            img = Image(image=frame)
            _, _, result = kekify(kek_param, filename, extension, img)
            new.sequence.append(result)
    return new


def multikek(filename, extension):
    w, h, canvasL = kekify("-l", filename, extension, None)
    w, h, canvasR = kekify("-r", filename, extension, None)
    w, h, canvasT = kekify("-t", filename, extension, None)
    w, h, canvasB = kekify("-b", filename, extension, None)
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
