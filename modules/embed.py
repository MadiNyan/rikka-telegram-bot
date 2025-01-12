import io
from itertools import chain

from telegram import Update
from telegram.ext import PrefixHandler
from wand.image import Image

from modules.logging import logging_decorator
from modules.utils import get_image, send_image, extract_first_frame, send_chat_action

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
    global launchpad_gif
    launchpad_gif = gd.config["launchpad_path"]
    commands = gd.config["commands"]
    gd.application.add_handler(PrefixHandler("/", commands, fap))


@logging_decorator("fap")
async def fap(update: Update, context):
    if update.message is None or update.message.reply_to_message is None:
        return
        
    try:
        # Get media
        file_bytes, mime_type, attachment_type, filename, has_spoiler = await get_image(update, context)
        if file_bytes is None:
            raise ValueError("Unable to retrieve the file.")

        await send_chat_action(update, context, "animation")

        # Extract first frame if media is video or gif
        if mime_type and (mime_type.startswith('video/') or mime_type == 'image/gif'):
            file_bytes = await extract_first_frame(file_bytes)

        # Resize source image
        with Image(blob=file_bytes.getvalue()) as decal:
            decal.resize(320, 172)
            w, h = decal.size
            decal.virtual_pixel = 'transparent'
            source_points = (
                (0, 0),
                (w, 0),
                (w, h),
                (0, h)
            )
            
            # Create result video object in memory
            result_bytes = io.BytesIO()
            
            # Open template gif and put source image on every frame
            with Image(filename=launchpad_gif) as template_gif:
                new = Image()
                for i in range(len(template_gif.sequence)):
                    img = Image(image=template_gif.sequence[i])
                    img.delay = 6
                    destination_points = (coords_by_frame[i])
                    order = chain.from_iterable(zip(source_points, destination_points))
                    arguments = list(chain.from_iterable(order))
                    decal_current = Image(image=decal)
                    decal_current.matte_color = "rgba(255, 255, 255, 0)"
                    decal_current.distort('perspective', arguments)
                    img.composite(decal_current, left=0, top=0)
                    new.sequence.append(img)
                    decal_current.close()
                    img.close()
                    
                # Save to BytesIO
                new.save(file=result_bytes)
                result_bytes.seek(0)
                
                # Send the result
                await send_image(update, result_bytes, "video/mp4", "animation", filename, None, has_spoiler)
                
                new.close()

    except Exception as e:
        await update.message.reply_text(f"Error during processing:\n{str(e)}")
