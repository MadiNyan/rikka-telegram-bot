import io
import random
import yaml

from PIL import Image, ImageChops, ImageOps
from telegram import Update, InputMediaPhoto
from telegram.ext import PrefixHandler

from modules.logging import logging_decorator
from modules.utils import get_image, get_param, extract_first_frame, send_chat_action

bleed = 100


def module_init(gd):
    global resources_path, templates_dict, templates_path
    resources_path = gd.config["resources_path"]
    templates_path = resources_path+"templates/"
    commands = gd.config["commands"]
    for command in commands:
        gd.application.add_handler(PrefixHandler("/", command, merch))
    with open(resources_path+"templates.yml", "r") as f:
        templates_dict = yaml.load(f, Loader=yaml.SafeLoader)


@logging_decorator("merch")
async def merch(update: Update, context):
    if update.message is None:
        return
    
    try:
        # Use new get_image function
        file_bytes, mime_type, attachment_type, filename, spoiler = await get_image(update, context)
        if file_bytes is None:
            raise ValueError("Unable to retrieve the file.")
        
        # Extract first frame if media is video or gif
        if mime_type and (mime_type.startswith('video/') or mime_type == 'image/gif'):
            file_bytes = await extract_first_frame(file_bytes)
            
        await send_chat_action(update, context, "photo")
        
        templates_list = list(templates_dict.keys())

        if len(context.args) > 0:
            if context.args[0] in templates_list:
                amount = 1
                template = True
            else:
                amount = await get_param(update, 1, 1, 10)
                template = False
        else:
            amount = await get_param(update, 1, 1, 10)
            template = False

        media_group = []
        for i in range(amount):
            if template is True:
                product = context.args[0]
            else:
                product = random.choice(templates_list)
            templates_list.remove(product)
            
            result_image = io.BytesIO()
            result_image = make_merch(file_bytes, result_image, templates_path, templates_dict[product], templates_dict[product]["offset"])

            # Create InputMediaPhoto object for each image
            media_group.append(InputMediaPhoto(media=result_image, has_spoiler=spoiler))

        # Send media group
        await update.message.reply_media_group(media=media_group)

        return amount
    except Exception as e:
        await update.message.reply_text(f"Error during processing:\n{str(e)}")
        return


def make_merch(input_bytes, output_bytes, templates_path, template, offset=(0,0)):
    # Load and prepare source template
    source = Image.open(templates_path + template["img"]).convert("RGBA")
    width, height = source.size
    long_side = max(width, height)

    # Load and prepare mask
    mask = Image.open(templates_path + template["mask"]).convert("RGBA")

    # Load and fit decal to mask size
    decal = ImageOps.fit(Image.open(input_bytes), mask.size, Image.Resampling.LANCZOS).convert("RGBA")

    # Create background
    bg = ImageOps.fit(
        Image.open(resources_path+"background.jpg"), 
        (long_side+bleed, long_side+bleed),
        Image.Resampling.LANCZOS
    )

    # Apply mask to decal and position it
    cutout = ImageChops.multiply(decal, mask)
    canvas = Image.new('RGBA', bg.size, (0,0,0,0))
    canvas.paste(cutout, offset, cutout)

    # Composite final product
    product = ImageChops.composite(
        ImageChops.multiply(canvas, source),
        source, 
        ImageChops.multiply(canvas, source)
    )
    
    # Paste product onto background
    bg.paste(product, ((bg.width-width)//2, (bg.height-height)//2), product)
    
    # Add watermark
    watermark = Image.open(resources_path+"watermark.png").convert("RGBA")
    bg.paste(watermark, (20, bg.height-watermark.height-20), watermark)

    # Save and return
    bg.convert("RGB").save(output_bytes, format='PNG')
    output_bytes.seek(0)
    return output_bytes
