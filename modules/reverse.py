import asyncio
import io
import os
import tempfile

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import PrefixHandler

from modules.logging import logging_decorator
from modules.utils import get_image, send_image


def module_init(gd):
    commands = gd.config["commands"]
    for command in commands:
        gd.application.add_handler(PrefixHandler("/", command, reverse))


@logging_decorator("reverse")
async def reverse(update: Update, context):
    if update.message is None:
        return

    try:
        # Get video
        file_bytes, mime_type, attachment_type, filename, has_spoiler = await get_image(update, context)
        if file_bytes is None:
            raise ValueError("Unable to retrieve the file")
            
        if not mime_type.startswith('video/') and not mime_type.startswith('image/gif'):
            raise ValueError("File must be a video")

        await update.message.chat.send_action(ChatAction.UPLOAD_VIDEO)

        # Create reversed video in memory
        result_bytes = await reverse_video(file_bytes)
        
        # Send the reversed video
        await send_image(update, result_bytes, mime_type, attachment_type, filename, None, has_spoiler)

    except Exception as e:
        await update.message.reply_text(f"Error during processing:\n{str(e)}")
        return


async def reverse_video(input_bytes):
    """Reverse a video using ffmpeg with shell=True for compatibility"""
    
    temp_input = None
    temp_output = None
    
    try:
        # Create temporary files with unique names and auto-cleanup
        temp_input = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        temp_output = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        
        # Write input to temporary file
        input_bytes.seek(0)
        temp_input.write(input_bytes.read())
        temp_input.close()  # Close but don't delete yet
        
        # Build ffmpeg command
        cmd = f'ffmpeg -loglevel panic -i "{temp_input.name}" -vf reverse -af areverse "{temp_output.name}" -y'
        
        # Run ffmpeg command
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise RuntimeError(f"FFmpeg error: {stderr.decode()}")
            
        # Read output file into BytesIO
        with open(temp_output.name, 'rb') as f:
            result_bytes = io.BytesIO(f.read())
            
        return result_bytes
        
    finally:
        # Ensure cleanup of temporary files
        if temp_input:
            try:
                temp_input.close()  # Make sure file is closed
                if os.path.exists(temp_input.name):
                    os.unlink(temp_input.name)
            except Exception as e:
                print(f"Error cleaning up input file: {e}")
                
        if temp_output:
            try:
                temp_output.close()  # Make sure file is closed
                if os.path.exists(temp_output.name):
                    os.unlink(temp_output.name)
            except Exception as e:
                print(f"Error cleaning up output file: {e}")
