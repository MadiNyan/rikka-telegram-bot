#!/usr/bin/python
# -*- coding: utf-8 -*-
import yaml

# import path
with open('config.yml', 'r') as f:
    glitch_folder = yaml.load(f)['path']['glitch']


# glitch processing; deleting lines in .jpg file
def process_img(bot, update):
    from random import randint
    import datetime
    with open(glitch_folder + 'original.jpg', 'rb') as f:
        linelist = list(f)
        linecount = len(linelist) - 10
        for i in range(5):
            i = randint(1, linecount - 1)
            linecount = linecount - 1
            del linelist[i]
    with open(glitch_folder + 'result.jpg', 'wb') as f:
        for content in linelist:
            f.write(content)
    with open(glitch_folder + 'result.jpg', 'rb') as f:
        bot.sendPhoto(update.message.chat_id, f,
                      reply_to_message_id=update.message.message_id)
    print (datetime.datetime.now(), '>>>', 'Done glitching', '>>>',
           update.message.from_user.username)


# checking if it is photo, reply with photo or reply with link
def glitch(bot, update):
    import requests
    import re
    if update.message.reply_to_message is not None:
        if '/glitch' in update.message.text:
            try:
                if 'http' in update.message.reply_to_message.text:
                    url = re.findall('http[s]?://\S+?\.(?:jpg|jpeg|png|gif)',
                                     update.message.reply_to_message.text)
                    link = str(url)
                    r = requests.get(link[2:-2])
                    with open(glitch_folder + 'original.jpg', 'wb') as code:
                        code.write(r.content)
                    process_img(bot, update)
                else:
                    photo = update.message.reply_to_message.photo[-1].file_id
                    bot.getFile(photo).download(glitch_folder + 'original.jpg')
                    process_img(bot, update)
            except:
                bot.sendMessage(update.message.chat_id,
                                text="I can't get the image!",
                                reply_to_message_id=update.message.message_id)
    elif '/glitch' in update.message.caption:
        photo = update.message.photo[-1].file_id
        bot.getFile(photo).download(glitch_folder + 'original.jpg')
        process_img(bot, update)
