#!/usr/bin/python
# -*- coding: utf-8 -*-
from telegram.ext import CommandHandler, Filters, Job, JobQueue
from datetime import datetime
from random import randint
import requests
import yaml
import os


def handler(dp):
    dp.add_handler(CommandHandler("sonyan", sonyan_post))

with open("config.yml", "r") as f:
    access_token = yaml.load(f)["keys"]["vk_token"]
with open("config.yml", "r") as f:
    channel = yaml.load(f)["keys"]["channel"]
owner = "-98881019"
count = "1"
offset = 0


def sonyan_post(bot, update):
    with open("resources/date.yml", "r") as datefile:
        date_old = yaml.load(datefile)["date"]
    date = check_post(owner, offset, count, access_token)

    if date > date_old:
        print("New post!")
        post_link, filename, text, pics_amount = dlpic(owner, offset, count, access_token)
    else:
        return

    if pics_amount == 1:
        images_text = text+"\n"+post_link
    else:
        images_text = text+"\n["+str(pics_amount)+" images] \n"+post_link

    with open("sonyan/"+filename, "rb") as file:
    	bot.sendPhoto(chat_id="@"+channel, photo=file, caption=images_text)
    data = {"date" : date}
    with open("resources/date.yml", "w") as datefile:
        yaml.dump(data, datefile)


def check_post(owner, offset, count, access_token):
    wallposts = requests.get("https://api.vk.com/method/wall.get?"+
                            "owner_id="+owner+
                             "&offset="+str(offset)+
                             "&count="+count+
                             "&filter="+owner+
                             "&access_token="+access_token+
                             "&v=5.60")
    serverjson = wallposts.json()
    date = serverjson["response"]["items"][0]["date"]
    return date

	
def dlpic(owner, offset, count, access_token):
    wallposts = requests.get("https://api.vk.com/method/wall.get?"+
                             "owner_id="+owner+
                             "&offset="+str(offset)+
                             "&count="+count+
                             "&filter="+owner+
                             "&access_token="+access_token+
                             "&v=5.60")
    serverjson = wallposts.json()

    id = serverjson["response"]["items"][0]["id"]
    text = serverjson["response"]["items"][0]["text"]
    post_link = "https://vk.com/wall-98881019_"+str(id)
    try:
        attachments = serverjson["response"]["items"][0]["attachments"]
    except:
        return None
    pics_amount = len(attachments)
    pic_to_get = randint(0, pics_amount-1)

    try:
        pic_link = serverjson["response"]["items"][0]["attachments"][pic_to_get]["photo"]["photo_2560"]
    except:
        try:
            pic_link = serverjson["response"]["items"][0]["attachments"][pic_to_get]["photo"]["photo_1280"]
        except:
            try:
                pic_link = serverjson["response"]["items"][0]["attachments"][pic_to_get]["photo"]["photo_807"]
            except:
                try:
                    pic_link = serverjson["response"]["items"][0]["attachments"][pic_to_get]["photo"]["photo_604"]
                except:
                    print("can't get link!")
                    return None

    dl = requests.get(pic_link)
    with open("sonyan/"+pic_link[-13:], "wb") as code:
        code.write(dl.content)

    return post_link, pic_link[-13:], text, pics_amount
