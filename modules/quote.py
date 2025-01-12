import io
import random

from PIL import Image, ImageDraw, ImageOps
from telegram import Update
from telegram.ext import PrefixHandler
from wand.color import Color
from wand.drawing import Drawing
from wand.font import Font
from wand.image import Image as wandImage

from modules.logging import logging_decorator
from modules.utils import send_image, send_chat_action


def module_init(gd):
    global resources_path, font_path
    resources_path = gd.config["resources_path"]
    font_path = gd.config["font"]
    commands = gd.config["commands"]
    gd.application.add_handler(PrefixHandler("/", commands, quote))


@logging_decorator("quote")
async def quote(update: Update, context):
    if update.message is None: return
    id, name, text = await get_message(update, context)
    if text == "" or text == None:
        await update.message.reply_text("Type in some text!")
        return
    await send_chat_action(update, context, "photo")
    profile_pic = await get_profile_pic(context, id, name)
    quote_image = make_quote(profile_pic, text, name)
    await send_image(update, quote_image, "image/jpeg", "photo", None)


def make_quote(profile_pic_bytes, text, author):
    # Load background and profile pic
    background = Image.open(resources_path+"bg.jpg")
    profile_pic_bytes.seek(0)
    avatar = Image.open(profile_pic_bytes)
    
    # Process images
    avatar_circle = circle(avatar)
    background.paste(avatar_circle, (50, 110), avatar_circle)
    watermark = Image.open(resources_path+"watermark.png").convert("RGBA")
    background.paste(watermark, (20, 540), watermark)
    
    # Convert to bytes and add text
    binary_image = img_to_bytes(background, ".jpg")
    output_bytes = fit_text(binary_image, text, author)
    return output_bytes


async def get_message(update, context):
    reply = update.message.reply_to_message
    if reply is None:
        id = update.message.from_user.id
        name = update.message.from_user.full_name
        if update.message.caption is not None:
            text = update.message.caption[3:]
        else:
            text = " ".join(context.args)
    else:
        if reply.forward_origin is None:
            id = reply.from_user.id
            name = reply.from_user.full_name
            if len(reply.photo) < 1:
                text = reply.text
            else:
                text = reply.caption
        else:
            id = reply.forward_origin.id
            name = reply.forward_origin.full_name
            if len(reply.photo) < 1:
                text = reply.text
            else:
                text = reply.caption
    return id, name, text


async def get_profile_pic(context, id, name):
    pics = await context.bot.getUserProfilePhotos(id, limit = 1)
    if len(pics.photos) == 0:
        return generate_profile_pic(name)
    else:
        user_profile_pics = await context.bot.getUserProfilePhotos(id, limit = 1)
        current_pfp = user_profile_pics.photos[0][-1].file_id
        dl_pfp = await context.bot.getFile(current_pfp)
        pfp_bytes = io.BytesIO()
        await dl_pfp.download_to_memory(pfp_bytes)
        return pfp_bytes


def generate_profile_pic(name):
    words = name.split()
    letters = [word[0] for word in words]
    initials = "".join(letters)
    colors =["#c75650", "#d67a27", "#7e6ccf", "#4eb331", "#2ea4ca"]
    pfp_bytes = io.BytesIO()
    with wandImage(width = 756, height = 756, background = Color(random.choice(colors))) as img:
        left, top, width, height = 200, 265, 340, 240
        with Drawing() as context:
            font = Font(font_path, color="white")
            context(img)
            img.caption(initials, left=left, top=top, width=width, height=height, font=font, gravity="center")
            img.save(file=pfp_bytes)
    pfp_bytes.seek(0)
    return pfp_bytes


def circle(image):
    mask = Image.open(resources_path+"mask.png").convert("L")
    circle = ImageOps.fit(image, mask.size, centering=(0.5, 0.5))
    circle.putalpha(mask)
    stroke = Image.new("RGBA", (756,756), (255,255,255,0))
    draw = ImageDraw.Draw(stroke)
    draw.ellipse((0, 0, 755, 755), width=18, outline ="white")
    stroke = stroke.resize((378, 378), resample=Image.Resampling.LANCZOS)
    circle.paste(stroke, (0,0), stroke)
    return circle


def img_to_bytes(file, ext):
	fp = io.BytesIO()
	format = Image.registered_extensions()[ext]
	file.save(fp, format)
	return fp.getvalue()


def fit_text(img, text, name):
    text = "«" + text + "»"
    name = "—  " + name
    output_bytes = io.BytesIO()
    with wandImage(blob=img) as canvas:
        text_left, text_top, text_width, text_height = 475, 50, 675, 410
        name_left, name_top, name_width, name_height = 530, 460, 570, 50
        with Drawing() as context:
            font = Font(font_path, color="white")
            context(canvas)
            canvas.caption(text, left=text_left, top=text_top, width=text_width, height=text_height, font=font, gravity="center")
            canvas.caption(name, left=name_left, top=name_top, width=name_width, height=name_height, font=font, gravity="center")
            canvas.save(file=output_bytes)
    output_bytes.seek(0)
    return output_bytes
