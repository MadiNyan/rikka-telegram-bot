#!/usr/bin/python
# -*- coding: utf-8 -*-
from modules.utils import caption_filter, get_image, send_image, get_param
from telegram.ext import CommandHandler, MessageHandler
from telegram.ext.dispatcher import run_async
from sklearn.cluster import KMeans
from telegram import ChatAction
from PIL import Image
import numpy as np
import datetime
import cv2


def module_init(gd):
    global path
    path = gd.config["path"]
    commands = gd.config["commands"]
    extensions = gd.config["extensions"]
    for command in commands:
        gd.dp.add_handler(MessageHandler(caption_filter("/"+command), palette))
        gd.dp.add_handler(CommandHandler(command, palette))


@run_async
def palette(bot, update):
    filename = datetime.datetime.now().strftime("%d%m%y-%H%M%S%f")
    name = filename + "-palette"
    colors = get_param(update, 4, 1, 10)
    if colors is None:
        return
    try:
        extension = get_image(bot, update, path, filename)
    except:
        update.message.reply_text("I can't get the image! :(")
        return
    update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
    start_computing(path, filename, extension, colors, "flat")
    send_image(update, path, name, extension)
    print(datetime.datetime.now(), ">>>", "palette", ">>>", update.message.from_user.username)


def start_computing(path, filename, extension, colors, mode):
    open_path = path + filename + extension
    number_of_colors = colors
    name = filename + "-palette"
    save_path = path + name + extension
    # Load image here
    pil_image = Image.open(open_path).convert('RGB')
    original_image = np.float32(pil_image)
    original_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)
    width, height = pil_image.size
    pil_image.thumbnail((400, 400), Image.ANTIALIAS)
    cv_image = np.float32(pil_image)
    # Reshape the image to be a list of pixels
    cv_image = cv_image.reshape((cv_image.shape[0] * cv_image.shape[1], 3))
    # Cluster the pixel intensities
    clt = KMeans(n_clusters = number_of_colors, tol=0.001).fit(cv_image)
    # Build a histogram of clusters representing the number of pixels labeled to each color
    hist = centroid_histogram(clt)
    bar = plot_colors(hist, clt.cluster_centers_, width, height, number_of_colors, mode)
    bar = cv2.cvtColor(bar, cv2.COLOR_BGR2RGB)
    # Separating line for image + palette stacking
    separator = np.zeros((15, width, 3), dtype = "uint8")
    separator = cv2.rectangle(separator, (0, 0), (width, 15), (30,30,30), -1)
    # Cobmine original image, separator and color chart
    stacked = np.concatenate((original_image, separator, bar), axis=0)
    stacked = cv2.cvtColor(stacked, cv2.COLOR_BGR2RGB)
    stacked = Image.fromarray(stacked.astype('uint8'))
    stacked.save(save_path)


def centroid_histogram(clt):
    numLabels = np.arange(0, len(np.unique(clt.labels_)) + 1)
    (hist, _) = np.histogram(clt.labels_, bins = numLabels)
    hist = hist.astype("float")
    hist /= hist.sum()
    return hist


def plot_colors(hist, centroids, width, height, number_of_colors, mode):
    bar_height = int(height*0.2)
    bar = np.zeros((bar_height, width, 3), dtype = "uint8")
    startX = 0
    for (percent, color) in zip(hist, centroids):
        if mode == "flat":
            endX = startX + (width/number_of_colors)
        elif mode == "percentage":
            endX = startX + (percent * width)
        cv2.rectangle(bar, (int(startX), 0), (int(endX), bar_height), color.astype("uint8").tolist(), -1)
        startX = endX
    return bar