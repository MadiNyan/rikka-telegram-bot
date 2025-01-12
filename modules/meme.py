import io
import textwrap

from PIL import Image, ImageDraw, ImageFont
from telegram import Update
from telegram.ext import PrefixHandler

from modules.logging import logging_decorator
from modules.utils import get_image, send_image, extract_first_frame, send_chat_action


def module_init(gd):
    global fonts_dict
    commands = gd.config["commands"]
    fonts_dict = {}
    for i in gd.config["fonts"]:
        fonts_dict[gd.config["fonts"][i]["name"]] = gd.config["fonts"][i]["path"]
    gd.application.add_handler(PrefixHandler("/", commands, meme))


def text_format(split_text):
    if len(split_text) == 1 and split_text[0] == "":
        return None, None
    elif len(split_text) > 1 and split_text[0] == "" and split_text[1] == "":
        return None, None
    elif len(split_text) == 1:
        top_text = None
        bottom_text = split_text[0]
        bottom_text.rstrip()
    elif len(split_text) > 1 and split_text[0] == "":
        top_text = None
        bottom_text = split_text[1]
        bottom_text.lstrip()
    elif len(split_text) > 1 and split_text[1] == "":
        top_text = split_text[0]
        top_text.rstrip()
        bottom_text = None
    else:
        top_text = split_text[0].rstrip()
        top_text.rstrip()
        bottom_text = split_text[1]
        bottom_text.lstrip()
    return top_text, bottom_text


@logging_decorator("meme")
async def meme(update: Update, context):
    if update.message is None:
        return

    args = context.args
    if len(args) < 1:
        await update.message.reply_text("Type in some text!")
        return

    # Get font
    font = fonts_dict["impact"]
    for i in fonts_dict:
        if "-"+i in args[0] or "-"+i[0] in args[0]:
            font = fonts_dict[i]
            args = args[1:]
            break

    initial_text = " ".join(args)
    split_text = initial_text.split("@", maxsplit=1)
    top_text, bottom_text = text_format(split_text)
    if top_text is None and bottom_text is None:
        await update.message.reply_text("Type in some text!")
        return

    try:
        # Get image using new function
        file_bytes, mime_type, attachment_type, filename, has_spoiler = await get_image(update, context)
        if file_bytes is None:
            raise ValueError("Unable to retrieve the file.")

        # Extract first frame if media is video or gif
        if mime_type and (mime_type.startswith('video/') or mime_type == 'image/gif'):
            file_bytes = await extract_first_frame(file_bytes)
            attachment_type = "photo"
        elif mime_type and not mime_type.startswith("image/"):
            raise ValueError("Unsupported media type.")
        
        await send_chat_action(update, context, "photo")

        # Generate meme
        result_bytes = await make_meme(top_text, bottom_text, file_bytes, font)

        # Send the processed image
        await send_image(update, result_bytes, mime_type, attachment_type, filename, None, has_spoiler)

    except Exception as e:
        await update.message.reply_text(f"Error during processing:\n{str(e)}")
        return

async def make_meme(topString, bottomString, input_bytes, meme_font):
    """
    Generate a meme from an image with top and bottom text
    
    Args:
        topString: Text for top of meme
        bottomString: Text for bottom of meme
        img: PIL Image object of the source image
        output_bytes: BytesIO object to write the result to
        meme_font: Path to the font file to use
    """
    img = Image.open(input_bytes)
    imageSize = img.size
    wrapwidth = int(imageSize[0]/20)

    # wrap input text strings
    if bottomString is None:
        bottomString = [" "]
    else:
        bottomString = textwrap.wrap(bottomString, width=wrapwidth)
    if topString is None:
        topString = [" "]
    else:
        topString = textwrap.wrap(topString, width=wrapwidth)
    
    # longest line to find font size
    longestTopString = max(topString, key=len)
    longestBottomString = max(bottomString, key=len)

    # find biggest font size that works
    fontSize = int(imageSize[1]/6)
    font = ImageFont.truetype(meme_font, fontSize)
    
    def get_text_size(text, font):
        bbox = font.getbbox(text)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]
    
    topTextSize = get_text_size(longestTopString, font)
    bottomTextSize = get_text_size(longestBottomString, font)
    
    # Ensure text fits within image width with padding
    while topTextSize[0] > imageSize[0]-20 or bottomTextSize[0] > imageSize[0]-20:
        fontSize = fontSize - 1
        font = ImageFont.truetype(meme_font, fontSize)
        topTextSize = get_text_size(longestTopString, font)
        bottomTextSize = get_text_size(longestBottomString, font)
        
    # find top centered position for top text
    topPositions = []
    initialX = 0 - topTextSize[1]
    for i in topString:
        topTextLineSize = get_text_size(i, font)
        topTextPositionX = (imageSize[0]/2) - (topTextLineSize[0]/2)
        topTextPositionY = initialX + topTextSize[1]
        initialX = topTextPositionY
        topTextPosition = (topTextPositionX, topTextPositionY)
        topPositions.append(topTextPosition)

    # find bottom centered position for bottom text
    bottomPositions = []
    # Calculate total height of bottom text block
    total_bottom_height = bottomTextSize[1] * len(bottomString)
    # Start from bottom with relative padding (10% of image height)
    bottom_padding = int(imageSize[1] * 0.1)  # 10% of image height
    initialY = imageSize[1] - total_bottom_height - bottom_padding
    
    for i in bottomString:
        bottomTextLineSize = get_text_size(i, font)
        bottomTextPositionX = (imageSize[0]/2) - (bottomTextLineSize[0]/2)
        bottomTextPositionY = initialY
        initialY = initialY + bottomTextSize[1]
        bottomTextPosition = (bottomTextPositionX, bottomTextPositionY)
        bottomPositions.append(bottomTextPosition)

    draw = ImageDraw.Draw(img)

    # draw outlines
    outlineRange = int(fontSize/25)+1
    for x in range(-outlineRange, outlineRange+1):
        for y in range(-outlineRange, outlineRange+1):
            ct = 0
            cb = 0
            for i in topPositions:
                draw.text((i[0]+x, i[1]+y), topString[ct], (0, 0, 0), font=font)
                ct += 1
            for i in bottomPositions:
                draw.text((i[0]+x, i[1]+y), bottomString[cb], (0, 0, 0), font=font)
                cb += 1

    for i in range(len(topString)):
        draw.text(topPositions[i], topString[i], (255, 255, 255), font=font)
    for i in range(len(bottomString)):
        draw.text(bottomPositions[i], bottomString[i], (255, 255, 255), font=font)

    # Save to the BytesIO object
    output_bytes = io.BytesIO()
    img.save(output_bytes, format='PNG')
    output_bytes.seek(0)
    return output_bytes
