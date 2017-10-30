#!/usr/bin/python
# -*- coding: utf-8 -*-
import subprocess
import os


# Cut & resize before processing
def cut_img(path, filename, extension):
    cut = "convert " + path + filename + extension + " ( +clone +level-colors white \
           ( +clone -rotate 90 +level-colors black ) \
           -composite -bordercolor white -border 1 -trim +repage ) +swap -compose Src \
           -gravity center -composite -resize 612x612 -extent 612x612 " + path + "temp" + extension
    subprocess.run(cut, shell=True)


# Add border of chosen color
def border(path, filename, extension, color):
    border = "convert  " + path + "temp" + extension + " -bordercolor " + color + " -border 20x20  " + path + "temp" + extension
    subprocess.run(border, shell=True)


# Add frame
def frame(path, filename, extension, file):
    frame = "convert  " + path + "temp" + extension + " resources/frames/" + file + ".png -geometry +0+0 \
             -composite  " + path + "temp" + extension
    subprocess.run(frame, shell=True)


# Vignette
def vignette(path, filename, extension, color1, color2):
    vignette = "convert " + path + "temp" + extension + " -size 918x918 radial-gradient:" + color1 + "-" + color2 + " \
                -gravity center -crop 612x612+0+0 +repage -compose multiply -flatten " + path + "temp" + extension
    subprocess.run(vignette, shell=True)


# Resize (if modified) and rename
def finish(path, extension, result_name):
    finish = "convert " + path + "temp" + extension + " -resize 612x612 " + path + result_name + extension
    subprocess.run(finish, shell=True)


# Filters to apply
def filt_Gotham(path, filename, extension):
    cut_img(path, filename, extension)
    primary_filter = "convert  " + path + "temp" + extension + " -modulate 120,10,100 -fill #222b6d \
                      -colorize 20 -gamma 0.5 -contrast -contrast  " + path + "temp" + extension
    subprocess.run(primary_filter, shell=True)
    border(path, filename, extension, "black")
    finish(path, extension, filename+"-gotham")
    remove_temp(path, extension)


def filt_Grayscale(path, filename, extension):
    cut_img(path, filename, extension)
    primary_filter = "convert  " + path + "temp" + extension + " -colorspace Gray " + path + "temp" + extension
    subprocess.run(primary_filter, shell=True)
    finish(path, extension, filename+"-grayscale")
    remove_temp(path, extension)


def filt_Kelvin(path, filename, extension):
    cut_img(path, filename, extension)
    primary_filter = "convert " + path + "temp" + extension + " -auto-gamma -modulate 120,50,100 \
              -size 612x612 -fill rgba(255,153,0,0.5) -draw \"rectangle 0,0 612,612\" \
              -compose multiply " + path + "temp" + extension
    subprocess.run(primary_filter, shell=True)
    frame(path, filename, extension, "kelvin")
    finish(path, extension, filename+"-kelvin")
    remove_temp(path, extension)


def filt_Lomo(path, filename, extension):
    cut_img(path, filename, extension)
    primary_filter = "convert " + path + "temp" + extension + " -channel R -level 25% \
             -channel G -level 25% " + path + "temp" + extension
    subprocess.run(primary_filter, shell=True)
    vignette(path, filename, extension, "none", "black")
    finish(path, extension, filename+"-lomo")
    remove_temp(path, extension)


def filt_Nashville(path, filename, extension):
    cut_img(path, filename, extension)
    primary_filter = "convert  " + path + "temp" + extension + " -contrast \
                      -modulate 100,150,100 -auto-gamma " + path + "temp" + extension
    subprocess.run(primary_filter, shell=True)
    color_overlay = "convert  " + path + "temp" + extension + " ( -clone 0 -fill #222b6d -colorize 100% ) \
                    ( -clone 0 -colorspace gray -negate ) -compose blend \
                    -define compose:args=50,50 -composite  " + path + "temp" + extension
    subprocess.run(color_overlay, shell=True)
    color_overlay2 = "convert  " + path + "temp" + extension + " ( -clone 0 -fill #f7daae -colorize 100% ) \
                    ( -clone 0 -colorspace gray ) -compose blend \
                    -define compose:args=120,-20 -composite  " + path + "temp" + extension
    subprocess.run(color_overlay2, shell=True)
    frame(path, filename, extension, "nashville")
    finish(path, extension, filename+"-nashville")
    remove_temp(path, extension)


def filt_Toaster(path, filename, extension):
    cut_img(path, filename, extension)
    color_overlay = "convert  " + path + "temp" + extension + " ( -clone 0 -fill #330000 -colorize 100% ) \
                    ( -clone 0 -colorspace gray -negate ) -compose blend \
                    -define compose:args=50,50 -composite  " + path + "temp" + extension
    subprocess.run(color_overlay, shell=True)
    primary_filter = "convert  " + path + "temp" + extension + " -modulate 150,80,100 -gamma 1.2 -contrast -contrast " + path + "temp" + extension
    subprocess.run(primary_filter, shell=True)
    vignette(path, filename, extension, "none", "LavenderBlush3")
    vignette(path, filename, extension, "#ff9966", "none")
    border(path, filename, extension, "white")
    finish(path, extension, filename+"-toaster")
    remove_temp(path, extension)


def filt_VHS(path, filename, extension):
    cut_img(path, filename, extension)
    red = "convert " + path + "temp" + extension + " -page +4+4 -background black -flatten -channel B -fx 0 " + path + "temp_r" + extension
    subprocess.run(red, shell=True)
    green = "convert " + path + "temp" + extension + " -channel R -fx 0 " + path + "temp_g" + extension
    subprocess.run(green, shell=True)
    blue = "convert " + path + "temp" + extension + " -page -4-4 -background black -flatten -channel G -fx 0 " + path + "temp_b" + extension
    subprocess.run(blue, shell=True)
    combine = "convert " + path + "temp_r" + extension + " " + path + "temp_g" + extension + " " + path + "temp_b" + extension + " -average " + path + "temp" + extension
    subprocess.run(combine, shell=True)
    frame(path, filename, extension, "scan")
    finish(path, extension, filename+"-VHS")
    remove_temp(path, extension, rgb=True)
    

def remove_temp(path, ext, rgb=False):
    os.remove(path+"temp"+ext)
    if rgb is True:
        os.remove(path+"temp_r"+ext)
        os.remove(path+"temp_g"+ext)
        os.remove(path+"temp_b"+ext)