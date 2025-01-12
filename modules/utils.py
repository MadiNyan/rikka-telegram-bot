import asyncio
import io
import magic
import mimetypes
import os
import re
import tempfile

from typing import Optional, Tuple
import requests
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatAction


# Function to extract URL from message entity
def extract_url(entity, text):
    if entity["type"] == "text_link":
        return entity["url"]
    elif entity["type"] == "url":
        offset = entity["offset"]
        length = entity["length"]
        return text[offset:offset+length]
    else:
        return None


# Function to handle URL extraction and download
async def process_url(url):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Get content type and file name from headers
        mime_type = response.headers.get('content-type')
        content_disp = response.headers.get('content-disposition')
        if content_disp:
            file_name = re.findall("filename=(.+)", content_disp)[0].strip('"')
        else:
            file_name = url.split('/')[-1]
        
        # Download the file
        file_bytes = io.BytesIO()
        for chunk in response.iter_content(chunk_size=8192):
            file_bytes.write(chunk)
        file_bytes.seek(0)
        
        # Determine file type
        if mime_type and mime_type.startswith('image/gif'):
            attachment_type = 'animation'
        elif mime_type and mime_type.startswith('image/'):
            attachment_type = 'photo'
        elif mime_type and mime_type.startswith('video/'):
            attachment_type = 'video'
        elif mime_type and mime_type.startswith('audio/'):
            attachment_type = 'audio'
        else:
            attachment_type = 'document'
            
        # Get actual mime type using magic
        mime_type = magic.Magic(mime=True).from_buffer(file_bytes.read(2048))
        file_bytes.seek(0)
        
        return file_bytes, mime_type, attachment_type, file_name, False
    except Exception as e:
        raise Exception(f"Error downloading from URL: {e}")


# Universal function to get media from message
async def get_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Tuple[Optional[io.BytesIO], str, str, str, bool]:
    if update.message is None:
        raise Exception("No message in update.")

    reply = update.message.reply_to_message

    if reply is None:
        return None, "", "", "", False

    # Check for URLs in replied message first
    if reply and reply.entities:
        for entity in reply.entities:
            url = extract_url(entity, reply.text)
            if url:
                result = await process_url(url)
                if result:
                    return result

    # Extract the file and determine its type
    if reply.photo:
        file = await context.bot.get_file(reply.photo[-1].file_id)
        attachment_type = "photo"
        has_spoiler = reply.has_media_spoiler
        file_name = reply.photo[-1].file_unique_id
        mime_type = "image/jpeg"
    elif reply.video:
        file = await context.bot.get_file(reply.video.file_id)
        attachment_type = "video"
        has_spoiler = reply.has_media_spoiler
        file_name = reply.video.file_name
        mime_type = reply.video.mime_type
    elif reply.sticker:
        file = await context.bot.get_file(reply.sticker.file_id)
        attachment_type = "sticker"
        has_spoiler = False
        if reply.sticker.is_animated:
            raise Exception("Animated stickers are not supported")
        if reply.sticker.is_video:
            file_name = reply.sticker.file_unique_id
            mime_type = "video/webm"
        else:
            file_name = reply.sticker.file_unique_id
            mime_type = "image/webp"
    elif reply.animation:
        file = await context.bot.get_file(reply.animation.file_id)
        attachment_type = "animation"
        file_name = reply.animation.file_name
        mime_type = reply.animation.mime_type
        has_spoiler = reply.has_media_spoiler
    elif reply.video_note:
        file = await context.bot.get_file(reply.video_note.file_id)
        attachment_type = "video_note"
        file_name = reply.video_note.file_unique_id
        mime_type = "video/mp4"
        has_spoiler = False
    elif reply.audio:
        file = await context.bot.get_file(reply.audio.file_id)
        attachment_type = "audio"
        file_name = reply.audio.file_name
        mime_type = reply.audio.mime_type
        has_spoiler = False
    elif reply.voice:
        file = await context.bot.get_file(reply.voice.file_id)
        attachment_type = "voice"
        file_name = reply.voice.file_unique_id
        mime_type = reply.voice.mime_type
        has_spoiler = False
    elif reply.document:
        file = await context.bot.get_file(reply.document.file_id)
        attachment_type = "document"
        file_name = reply.document.file_name
        mime_type = reply.document.mime_type
        has_spoiler = False
    else:
        raise Exception("No valid media found in reply message.")

    file_data = await file.download_as_bytearray()
    file_bytes = io.BytesIO(file_data)
    file_bytes.seek(0)

    # Retrieve MIME type if none is provided
    if mime_type is None:
        mime_type = magic.Magic(mime=True).from_buffer(file_bytes.read(2048))
        file_bytes.seek(0)

    # Retrieve file name from file path if not already set
    if not file_name and file.file_path:
        file_name = os.path.basename(file.file_path)

    # Add default values for returns
    file_name = file_name or "file"
    mime_type = mime_type or "application/octet-stream"
    attachment_type = attachment_type or "document"
    has_spoiler = has_spoiler or False
    
    return file_bytes, mime_type, attachment_type, file_name, has_spoiler


async def send_image(
        update: Update, 
        file_bytes: io.BytesIO, 
        mime_type: str, 
        attachment_type: str, 
        file_name: Optional[str], 
        caption: Optional[tuple] = (None),
        has_spoiler: bool = False
        ):
    if update.message is None:
        return
    if caption is None:
        caption = (None, None)
    
    file_bytes.seek(0)  # Reset the file pointer for sending

    # Guess the file extension if not provided
    extension = mimetypes.guess_extension(mime_type, strict=False)
    if not extension and file_name:
        extension = os.path.splitext(file_name)[1]  # Use extension from filename

    # Attach a filename with extension
    if file_name and extension:
        file_name = os.path.splitext(file_name)[0] + extension  # Ensure the correct extension
    elif extension:
        file_name = f"file{extension}"

    # Prepare file for sending with name
    file_bytes.name = file_name or "file"

    print("File bytes: ", file_bytes, "\n"
          "mime_type: ", mime_type, "\n"
          "attachment_type: ", attachment_type, "\n"
          "file_name: ", file_name, "\n"
          "caption: ", caption, "\n"
          "has_spoiler: ", has_spoiler, "\n",
          "file_bytes.size: ", file_bytes.getbuffer().nbytes)

    # Handle sending based on attachment type with spoiler support
    if attachment_type == "photo":
        await update.message.reply_photo(file_bytes, caption=caption[0], parse_mode=caption[1], has_spoiler=has_spoiler)
    elif attachment_type == "video":
        await update.message.reply_video(file_bytes, caption=caption[0], parse_mode=caption[1], has_spoiler=has_spoiler)
    elif attachment_type == "sticker":
        await update.message.reply_sticker(file_bytes)
    elif attachment_type == "animation":
        await update.message.reply_animation(file_bytes, caption=caption[0], parse_mode=caption[1], has_spoiler=has_spoiler)
    elif attachment_type == "video_note":
        await update.message.reply_video_note(file_bytes)
    elif attachment_type == "audio":
        await update.message.reply_audio(file_bytes, caption=caption[0], parse_mode=caption[1])
    elif attachment_type == "voice":
        await update.message.reply_voice(file_bytes, caption=caption[0], parse_mode=caption[1])
    elif attachment_type == "document":
        await update.message.reply_document(file_bytes, caption=caption[0], parse_mode=caption[1])
    else:
        # Fallback for unknown file types
        await update.message.reply_document(file_bytes, caption=caption[0], parse_mode=caption[1])


async def get_param(update, defaultvalue, min_value, max_value):
    if update.message.reply_to_message is not None:
        parts = update.message.text.split(" ", 1)
    elif update.message.caption is not None:
        parts = update.message.caption.split(" ", 1)
    elif update.message.text is not None:
        parts = update.message.text.split(" ", 2)
    else:
        return defaultvalue
    if len(parts) == 1:
        parameter = defaultvalue
    else:
        try:
            parameter = int(parts[1])
        except:
            #update.message.reply_text("Paremeter needs to be a number!")
            return defaultvalue
        if  parameter < min_value or parameter > max_value:
            errtext = "Baka, make it from " + str(min_value) + " to " + str(max_value) + "!"
            await update.message.reply_text(errtext)
            return 0
    return parameter


async def extract_first_frame(file_bytes):
    """Extract first frame from video or gif"""
    
    # Create temporary input file
    temp_input = None
    
    try:
        # Create temporary file with unique name
        temp_input = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        
        # Write input to temporary file
        file_bytes.seek(0)
        temp_input.write(file_bytes.read())
        temp_input.close()  # Close but don't delete yet
        
        # Build ffmpeg command
        cmd = f'ffmpeg -loglevel panic -i "{temp_input.name}" -vframes 1 -f image2pipe -vcodec png pipe:1'
        
        # Run ffmpeg command
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise RuntimeError("FFmpeg failed extracting frame")
            
        # Return the extracted frame
        frame_file_bytes = io.BytesIO(stdout)
        return frame_file_bytes
        
    finally:
        # Ensure cleanup of temporary file
        if temp_input:
            try:
                temp_input.close()  # Make sure file is closed
                if os.path.exists(temp_input.name):
                    os.unlink(temp_input.name)
            except Exception as e:
                print(f"Error cleaning up input file: {e}")


async def send_chat_action(update: Update, context: ContextTypes.DEFAULT_TYPE, attachment_type: str):
    if update.message is None:
        return
    if attachment_type == "photo":
        await update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
    elif attachment_type == "video":
        await update.message.chat.send_action(ChatAction.UPLOAD_VIDEO)
    elif attachment_type == "animation":
        await update.message.chat.send_action(ChatAction.UPLOAD_VIDEO)
    elif attachment_type == "sticker":
        await update.message.chat.send_action(ChatAction.CHOOSE_STICKER)
    elif attachment_type == "video_note":
        await update.message.chat.send_action(ChatAction.UPLOAD_VIDEO_NOTE)
    elif attachment_type == "voice":
        await update.message.chat.send_action(ChatAction.RECORD_VOICE)
    elif attachment_type == "audio":
        await update.message.chat.send_action(ChatAction.UPLOAD_VOICE)
    elif attachment_type == "document":
        await update.message.chat.send_action(ChatAction.UPLOAD_DOCUMENT)
    else:
        await update.message.chat.send_action(ChatAction.TYPING)
