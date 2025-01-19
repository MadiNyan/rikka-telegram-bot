import io
import asyncio

from concurrent.futures import ThreadPoolExecutor
from telegram import Update
from telegram.ext import PrefixHandler
from wand.image import Image

from modules.logging import logging_decorator
from modules.utils import get_image, get_param, send_image, send_chat_action

executor = ThreadPoolExecutor(max_workers=4)


def module_init(gd):
    commands = gd.config["commands"]
    gd.application.add_handler(PrefixHandler("/", commands, liquid))


def process_image(file_bytes, power, w, h, is_video_frame=False):
    new = Image()
    with Image(blob=file_bytes, format='PNG' if is_video_frame else None) as original:
        for frame in original.sequence:
            img = Image(image=frame)
            img.liquid_rescale(int(w * power), int(h * power), delta_x=1)
            img.resize(w, h)
            new.sequence.append(img)
            img.close()
    
    output = io.BytesIO()
    new.save(file=output)
    output.seek(0)
    new.close()
    return output


@logging_decorator("liq")
async def liquid(update: Update, context):
    if update.message is None:
        return

    # Get the power parameter
    power = await get_param(update, 50, -100, 100)
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
        if mime_type is not None and mime_type.startswith("video/"):
            # Send initial progress message as a reply
            progress_message = await update.message.reply_text("Processing... 0 frames")
            
            # Handle MP4
            with Image(blob=file_bytes.read(), format="mp4") as original:
                w, h = original.size
                total_frames = len(original.sequence)
                processed_frames = []
                
                # Store original animation properties
                delay = original.sequence[0].delay
                
                for i, frame in enumerate(original.sequence):
                    if i % 10 == 0:  # Update every 10 frames
                        await progress_message.edit_text(f"Processing... {i}/{total_frames} frames")
                    
                    # Process frame in thread pool
                    frame_bytes = io.BytesIO()
                    with Image(image=frame) as frame_img:
                        frame_img.format = 'PNG'  # Set format explicitly
                        frame_img.save(frame_bytes)
                    frame_bytes.seek(0)
                    
                    future = executor.submit(
                        process_image,
                        frame_bytes.getvalue(),
                        power,
                        w,
                        h,
                        True  # Indicate this is a video frame
                    )
                    processed_frames.append(future)
                
                # Wait for all frames to be processed
                processed_frames = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: [future.result() for future in processed_frames]
                )
                
                # Combine frames
                new = Image()
                for frame_data in processed_frames:
                    with Image(blob=frame_data.getvalue()) as frame:
                        frame.delay = delay  # Restore original delay
                        new.sequence.append(frame.sequence[0])
                
                processed_file_bytes = io.BytesIO()
                new.format = original.format  # Preserve original format
                new.save(file=processed_file_bytes)
                processed_file_bytes.seek(0)
                new.close()
                
                # Delete progress message after completion
                await progress_message.delete()
        else:
            # Handle single image in thread pool
            with Image(blob=file_bytes.read()) as original:
                w, h = original.size
                processed_file_bytes = await asyncio.get_event_loop().run_in_executor(
                    executor,
                    process_image,
                    file_bytes.getvalue(),
                    power,
                    w,
                    h
                )

        # Send the processed file back to the user
        await send_image(update, processed_file_bytes, mime_type, attachment_type, filename, None, spoiler)

    except Exception as e:
        await update.message.reply_text(f"Error during processing:\n{str(e)}")
    finally:
        file_bytes.close()
