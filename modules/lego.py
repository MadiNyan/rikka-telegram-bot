from PIL import Image
from pkg_resources import parse_version

# Add compatibility for Pillow 10.0.0+
if parse_version(Image.__version__) >= parse_version('10.0.0'):
    Image.ANTIALIAS = Image.LANCZOS

import os
import tempfile
import io
import legofy

from telegram import Update
from telegram.ext import PrefixHandler

from modules.logging import logging_decorator
from modules.utils import get_image, get_param, send_image, extract_first_frame, send_chat_action


def module_init(gd):
    commands = gd.config["commands"]
    gd.application.add_handler(PrefixHandler("/", commands, lego))


@logging_decorator("lego")
async def lego(update: Update, context):
    if update.message is None:
        return

    size = await get_param(update, 35, 1, 100)
    if size is None:
        return

    # Create temporary directory for processing
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Get image using new function
            file_bytes, mime_type, attachment_type, filename, has_spoiler = await get_image(update, context)
            if file_bytes is None:
                raise ValueError("Unable to retrieve the file.")
            
            # Extract first frame if media is video or gif
            if mime_type and (mime_type.startswith('video/') or mime_type == 'image/gif'):
                file_bytes = await extract_first_frame(file_bytes)
                attachment_type = "photo"
                mime_type = "image/jpeg"

            await send_chat_action(update, context, attachment_type)

            # Process image
            img = Image.open(file_bytes)
            
            # Handle transparency for webp and png
            if mime_type in ["image/webp", "image/png"]:
                # Create white background
                bg = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode in ('RGBA', 'LA'):
                    bg.paste(img, mask=img.split()[-1])
                else:
                    bg.paste(img)
                img = bg

            # Save input image to temp file
            input_path = os.path.join(temp_dir, "input.png")
            img.save(input_path, format='PNG')

            # Process with legofy
            output_path = os.path.join(temp_dir, "output.png")
            legofy.main(image_path=input_path,
                       output_path=output_path,
                       size=size,
                       palette_mode=None,
                       dither=False)

            # Read the result back into memory
            with open(output_path, 'rb') as f:
                result_bytes = io.BytesIO(f.read())

            # Send the processed image
            await send_image(update, result_bytes, mime_type, attachment_type, filename, None, has_spoiler)

        except Exception as e:
            await update.message.reply_text(f"Error during processing:\n{str(e)}")
            return
