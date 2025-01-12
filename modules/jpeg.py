import io

from PIL import Image
from telegram import Update
from telegram.ext import PrefixHandler

from modules.logging import logging_decorator
from modules.utils import get_image, get_param, send_image, extract_first_frame, send_chat_action


def module_init(gd):
    commands = gd.config["commands"]
    gd.application.add_handler(PrefixHandler("/", commands, jpeg))


@logging_decorator("jpeg")
async def jpeg(update: Update, context):
    if update.message is None:
        return

    compress = await get_param(update, 6, 1, 10)
    if compress == 0:
        return
    compress = 11 - compress

    try:
        # Get image using new function
        file_bytes, mime_type, attachment_type, filename, spoiler = await get_image(update, context)
        if file_bytes is None:
            raise ValueError("Unable to retrieve the file.")
        
        # Extract first frame if media is video or gif
        if mime_type and (mime_type.startswith('video/') or mime_type == 'image/gif'):
            file_bytes = await extract_first_frame(file_bytes)
            attachment_type = "photo"
            mime_type = "image/jpeg"

        await send_chat_action(update, context, attachment_type)

        # Process image in memory
        result_bytes = io.BytesIO()
        original = Image.open(file_bytes)

        if mime_type == "image/jpeg":
            original.save(result_bytes, format='JPEG', quality=compress, optimize=True)
        else:
            # Handle transparency
            rgb_im = original.convert('RGB')
            compressed = io.BytesIO()
            rgb_im.save(compressed, format='JPEG', quality=compress, optimize=True)
            compressed.seek(0)
            foreground = Image.open(compressed)
            
            try:
                original.paste(foreground, (0, 0), original)
            except:
                pass
                
            original.save(result_bytes, format=original.format)

        result_bytes.seek(0)
        
        # Send the processed image
        await send_image(update, result_bytes, mime_type, attachment_type, filename, None, spoiler)

    except Exception as e:
        await update.message.reply_text(f"Unable to process the image.\nError: {str(e)}")
        return
