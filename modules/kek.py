import mimetypes
import io

from telegram import Update
from telegram.ext import PrefixHandler
from wand.image import Image

from modules.logging import logging_decorator
from modules.utils import get_image, send_image, send_chat_action


def module_init(gd):
    commands = gd.config["commands"]
    gd.application.add_handler(PrefixHandler("/", commands, kek))


@logging_decorator("kek")
async def kek(update: Update, context):
    if update.message is None:
        return
    kek_param = context.args[0] if len(context.args) > 0 else ""

    try:
        # Get image
        file_bytes, mime_type, attachment_type, filename, has_spoiler = await get_image(update, context)
        if file_bytes is None:
            raise ValueError("Unable to retrieve the file.")
            
        # Get extension from mime type
        extension = mimetypes.guess_extension(mime_type, strict=False) or ".png"
            
        await send_chat_action(update, context, attachment_type)
        
        # Process the image
        if mime_type and mime_type.startswith("video/") or mime_type.startswith("image/gif"):
            if kek_param == "-m":
                raise ValueError("Multikek unsupported for animations")
            result = await kekify_gifs(kek_param, file_bytes, extension)
        elif mime_type and mime_type.startswith("image/"):
            _, _, result = await kekify(kek_param, file_bytes, None)
        else:
            raise ValueError("Unsupported file type.")
            
        # Save result to bytes with format
        result_bytes = io.BytesIO()
        format_type = extension.lstrip('.').upper()
        result.format = format_type  # Set format before saving
        result.save(file=result_bytes)
        result_bytes.seek(0)
        result.close()
        
        # Send the result
        await send_image(update, result_bytes, mime_type, attachment_type, filename, None, has_spoiler)
        
    except Exception as e:
        await update.message.reply_text(f"Error processing image:\n{str(e)}")
        return


async def kekify(kek_param, file_bytes, file):
    if kek_param == "-m":
        result = await multikek(file_bytes)
        return None, None, result

    if file is None:
        source = Image(blob=file_bytes.getvalue())
    else:
        source = file

    w = source.width; h = source.height
    c, p1, p2, f = await get_values(kek_param, w, h)
    
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
    

async def kekify_gifs(kek_param, file_bytes, extension):
    # Specify format when creating image from bytes
    format_type = extension.lstrip('.').upper()
    with Image(blob=file_bytes.getvalue(), format=format_type) as source:
        w = source.width; h = source.height
        new = Image()
        for frame in source.sequence:
            img = Image(image=frame)
            _, _, result = await kekify(kek_param, file_bytes, img)
            new.sequence.append(result)
    return new


async def multikek(file_bytes):
    w, h, canvasL = await kekify("-l", file_bytes, None)      
    w, h, canvasR = await kekify("-r", file_bytes, None)
    w, h, canvasT = await kekify("-t", file_bytes, None)
    w, h, canvasB = await kekify("-b", file_bytes, None)
    
    if w is None or h is None:
        raise ValueError("Failed to get image dimensions")
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


async def get_values(kek_param, w, h):
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
