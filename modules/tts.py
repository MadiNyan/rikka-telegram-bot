import asyncio
import io
import os
import tempfile
import comtypes.client

from telegram import Update
from telegram.ext import PrefixHandler, ContextTypes

from modules.logging import logging_decorator
from modules.utils import send_chat_action


def module_init(gd):
    commands = gd.config["commands"]
    for command in commands:
        gd.application.add_handler(PrefixHandler("/", command, tts))


# Helper function to convert WAV to OGG opus
async def convert_wav_to_ogg_async(wav_path, ogg_path):
    cmd = f"ffmpeg -i {wav_path} -acodec libopus -ac 1 -ar 16000 {ogg_path} -y"
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        raise Exception(f"FFmpeg error")


@logging_decorator("say")
async def tts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return

    # Get text to speak
    reply = update.message.reply_to_message
    if reply is None:
        text = " ".join(context.args) if context.args else None
    elif reply.text is not None:
        text = reply.text
    else:
        return

    if not text:
        await update.message.reply_text("Type in some text")
        return

    await send_chat_action(update, context, "voice")

    # Create temporary files
    temp_wav = None
    temp_ogg = None
    try:
        # Initialize COM
        comtypes.CoInitialize()

        # Create temporary files
        temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        temp_wav.close()
        temp_ogg = tempfile.NamedTemporaryFile(delete=False, suffix='.ogg')
        temp_ogg.close()

        # Set up SAPI for text-to-speech
        speak = comtypes.client.CreateObject("SAPI.SpVoice")
        filestream = comtypes.client.CreateObject("SAPI.SpFileStream")
        filestream.Open(temp_wav.name, 3, False)  # 3 = SSFMCreateForWrite
        speak.AudioOutputStream = filestream
        speak.Speak(text)
        filestream.Close()

        # Convert WAV to OGG (Opus) using asyncio
        await convert_wav_to_ogg_async(temp_wav.name, temp_ogg.name)

        # Read the OGG file into BytesIO
        with open(temp_ogg.name, 'rb') as f:
            voice_bytes = io.BytesIO(f.read())

        # Send the voice message
        await update.message.reply_voice(voice_bytes, quote=False)

    except Exception as e:
        await update.message.reply_text(f"Error during processing:\n{str(e)}")

    finally:
        # Cleanup
        comtypes.CoUninitialize()
        for temp_file in [temp_wav, temp_ogg]:
            if temp_file and os.path.exists(temp_file.name):
                try:
                    os.unlink(temp_file.name)
                except Exception as e:
                    print(f"Error cleaning up temp file {temp_file.name}: {e}")