import io

from telegram import Update
from telegram.ext import PrefixHandler
from wand.image import Image

from modules.logging import logging_decorator
from modules.utils import get_image, get_param, send_image, send_chat_action


def module_init(gd):
    commands = gd.config["commands"]
    gd.application.add_handler(PrefixHandler("/", commands, liquid))


@logging_decorator("liq")
async def liquid(update: Update, context):
    if update.message is None:
        return

    # Get the power parameter
    power = await get_param(update, 60, -100, 100)
    if power is None:
        return

    try:
        # Retrieve the image/video as in-memory bytes and MIME type
        file_bytes, mime_type, attachment_type, filename, spoiler = await get_image(update, context)
        if file_bytes is None:
            raise ValueError("Unable to retrieve the file.")
    except Exception as e:
        await update.message.reply_text(f"Unable to retrieve the file.\nError: {str(e)}")
        return

    # Calculate rescaling power
    power = (100 - (power / 1.3)) / 100

    # Send an upload photo/video action
    await send_chat_action(update, context, attachment_type)

    if mime_type is not None and mime_type.startswith("application/"):
        extension = filename.split(".")[-1]
        if extension == "mp4":
            mime_type = "video/mp4"

    try:
        processed_file_bytes = io.BytesIO()

        if mime_type is not None and mime_type.startswith("video/"):
            # Send initial progress message as a reply
            progress_message = await update.message.reply_text("Processing... 0 frames")
            
            # Handle MP4
            with Image(blob=file_bytes.read(), format="mp4") as original:
                w, h = original.size
                total_frames = len(original.sequence)
                new = Image()
                for i, frame in enumerate(original.sequence):
                    # Process frame
                    if i % 10 == 0:  # Update every 10 frames
                        await progress_message.edit_text(f"Processing... {i}/{total_frames} frames")
                    img = Image(image=frame)
                    img.liquid_rescale(int(w * power), int(h * power), delta_x=1)
                    img.resize(w, h)
                    new.sequence.append(img)
                    img.close()
                # Save the processed video to in-memory bytes
                new.save(file=processed_file_bytes)
                processed_file_bytes.seek(0)
                new.close()
                # Delete progress message after completion
                await progress_message.delete()
        else:
            # Handle images
            with Image(blob=file_bytes.read()) as original:
                w, h = original.size
                new = Image()
                for frame in original.sequence:
                    img = Image(image=frame)
                    img.liquid_rescale(int(w * power), int(h * power), delta_x=1)
                    img.resize(w, h)
                    new.sequence.append(img)
                    img.close()
                # Save the processed image to in-memory bytes
                new.save(file=processed_file_bytes)
                processed_file_bytes.seek(0)
                new.close()

        # Send the processed file back to the user
        await send_image(update, processed_file_bytes, mime_type, attachment_type, filename, None, spoiler)

    except Exception as e:
        await update.message.reply_text(f"Error during processing: {e}")
    finally:
        file_bytes.close()
