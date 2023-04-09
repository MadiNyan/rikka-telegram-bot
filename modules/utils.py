import os.path
import subprocess

import requests
from telegram import Update
from telegram.ext import ContextTypes
from telegram.ext.filters import BaseFilter


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
    if path is None:
        return False
    ext = None
    image_extensions = (".jpg", ".jpeg", ".png", ".gif", ".svg", ".tif", ".bmp", ".mp4")
    if path is None:
        return False
    for i in image_extensions:
        if path.casefold().endswith(i):
            ext = i
            return ext
    if ext == None:
        ext = ".mp4"
        return ext
    return False

def is_image_by_mime_type(mime_type):
    if mime_type is None:
        return False
    mime_types = {
        "image/png": ".png",
        "image/gif": ".gif",
        "image/jpeg": ".jpg",
        "video/mp4": ".mp4",
    }
    return mime_types.get(mime_type.casefold(), False)


async def get_image(update: Update, context: ContextTypes.DEFAULT_TYPE, dl_path, filename):
    if update.message is None: return
    output = os.path.join(dl_path, filename)
    reply = update.message.reply_to_message
    if reply is None:
        extension = ".jpg"
        await (await context.bot.getFile(update.message.photo[-1].file_id)).download_to_drive(output + extension)
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
    # Document with file name
    if reply.document is not None and is_image(reply.document.file_name):
        extension = is_image(reply.document.file_name)
        await (await context.bot.getFile(reply.document.file_id)).download_to_drive(output + extension)
        return extension
    # Document without file name
    if reply.document is not None and is_image_by_mime_type(reply.document.mime_type):
        extension = is_image_by_mime_type(reply.document.mime_type)
        await (await context.bot.getFile(reply.document.file_id)).download_to_drive(output + extension)
        return extension
    # Sticker
    if reply.sticker is not None:
        extension = ".webp"
        await (await context.bot.getFile(reply.sticker.file_id)).download_to_drive(output+extension)
        return extension
    # Video in reply
    if reply.video is not None:
        extension = ".mp4"
        await (await context.bot.getFile(reply.video.file_id)).download_to_drive(output + extension)
        return extension
    # Photo in reply
    if reply.photo is not None:
        extension = ".jpg"
        await (await context.bot.getFile(reply.photo[-1].file_id)).download_to_drive(output + extension)
        return extension
    return False


async def send_image(update: Update, filepath, name, extension):
    if update.message is None: return
    photo_extensions = (".jpg", ".jpeg")
    doc_extensions = (".png", ".svg", ".tif", ".bmp", ".gif", ".mp4")
    sticker_extensions = (".webp")
    if extension in photo_extensions:
        with open(filepath + name + extension, "rb") as f:
            await update.message.reply_photo(f)
        return True  
    if extension in doc_extensions:
        with open(filepath + name + extension, "rb") as f:
            await update.message.reply_document(f)
        return True
    if extension in sticker_extensions:
        with open(filepath + name + extension, "rb") as f:
            await update.message.reply_sticker(f)
        return True


async def get_param(update, defaultvalue, min_value, max_value):
    if update.message.reply_to_message is not None:
        parts = update.message.text.split(" ", 1)
    elif update.message.caption is not None:
        parts = update.message.caption.split(" ", 1)
    elif update.message.text is not None:
        parts = update.message.text.split(" ", 2)
    else:
        return defaultvalue
    if len(parts) == 1:
        parameter = defaultvalue
    else:
        try:
            parameter = int(parts[1])
        except:
            #update.message.reply_text("Paremeter needs to be a number!")
            return defaultvalue
        if  parameter < min_value or parameter > max_value:
            errtext = "Baka, make it from " + str(min_value) + " to " + str(max_value) + "!"
            await update.message.reply_text(errtext)
            return 0
    return parameter
    
def mp4_fix(path, filename):
    args = "ffmpeg -loglevel panic -i " + path + filename + ".mp4" + \
            " -an -vf scale=trunc(iw/2)*2:trunc(ih/2)*2 \
            -pix_fmt yuv420p -c:v libx264 -profile:v high -level:v 2.0 " \
            + path + filename + "fixed.mp4 -y"
    subprocess.run(args, shell=True)
    os.remove(path+filename+".mp4")
    fixed_file_name = filename + "fixed"
    return fixed_file_name


# custom filters for message handler
# photo with caption
class Caption_Filter(BaseFilter):
    def __init__(self, command):
        self.data=command
    def filter(self, message):
        if message.photo and message.caption and message.caption.startswith(self.data):
            return True
