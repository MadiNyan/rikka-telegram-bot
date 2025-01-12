import io
import cv2
import numpy as np

from PIL import Image
from sklearn.cluster import KMeans
from telegram import Update
from telegram.ext import PrefixHandler

from modules.logging import logging_decorator
from modules.utils import get_image, get_param, send_image, extract_first_frame, send_chat_action


def module_init(gd):
    commands = gd.config["commands"]
    gd.application.add_handler(PrefixHandler("/", commands, palette))


@logging_decorator("palette")
async def palette(update: Update, context):
    if update.message is None: return
    colors = await get_param(update, 4, 1, 10)
    if colors is None:
        return
    try:
        # Get image
        file_bytes, mime_type, attachment_type, filename, spoiler = await get_image(update, context)
        if file_bytes is None:
            raise ValueError("Unable to retrieve the file.")
    
        # Extract first frame if media is video or gif
        if mime_type and (mime_type.startswith('video/') or mime_type == 'image/gif'):
            file_bytes = await extract_first_frame(file_bytes)
        
        await send_chat_action(update, context, "photo")

        # Calculate palette
        processed_file_bytes = await start_computing(file_bytes, colors, "percentage")
        # Send the processed file back to the user
        await send_image(update, processed_file_bytes, mime_type, "photo", filename, None, spoiler)
        return colors

    except Exception as e:
        await update.message.reply_text(f"Error during processing:\n{str(e)}")
        return


async def start_computing(file_bytes, colors, mode):
    # Load and process image
    original = Image.open(file_bytes).convert('RGB')
    width, height = original.size
    
    # Create small copy for clustering
    small_img = original.copy()
    small_img.thumbnail((400, 400), Image.Resampling.LANCZOS)
    pixels = np.float32(np.array(small_img)).reshape(-1, 3)
    
    # Cluster colors
    clt = KMeans(n_clusters=colors, tol=0.001, n_init="auto").fit(pixels)
    hist = await centroid_histogram(clt)
    
    # Generate color bar
    bar = await plot_colors(hist, clt.cluster_centers_, width, height, colors, mode)
    
    # Stack images
    separator = np.full((15, width, 3), 30, dtype="uint8")
    stacked = np.concatenate((np.array(original), np.array(separator), np.array(bar)), axis=0)
    
    # Convert and save result
    result = Image.fromarray(stacked.astype('uint8'))
    output = io.BytesIO()
    result.save(output, format="PNG")
    
    # Cleanup
    original.close()
    small_img.close()
    result.close()
    
    return output


async def centroid_histogram(clt):
    numLabels = np.arange(0, len(np.unique(clt.labels_)) + 1)
    (hist, _) = np.histogram(clt.labels_, bins = numLabels)
    hist = hist.astype("float")
    hist /= hist.sum()
    return hist


async def plot_colors(hist, centroids, width, height, number_of_colors, mode):
    bar_height = int(height*0.2)
    bar = np.zeros((bar_height, width, 3), dtype = "uint8")
    startX = 0
    for (percent, color) in zip(hist, centroids):
        if mode == "flat":
            endX = startX + (width/number_of_colors)
        elif mode == "percentage":
            endX = startX + (percent * width)
        else:
            return None
        cv2.rectangle(bar, (int(startX), 0), (int(endX), bar_height), color.astype("uint8").tolist(), -1)
        startX = endX
    return bar