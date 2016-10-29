import requests
import subprocess


def get_image(bot, update, dl_path):
    if update.message.reply_to_message is not None:
        # Entities; url, text_link
        if update.message.reply_to_message.entities is not None:
            if len(update.message.reply_to_message.entities) != 0:
                entity = update.message.reply_to_message.entities
                for i in range(0, len(entity)):
                    type = entity[i]["type"]
                    if type == "text_link":
                        if entity[i]["url"].endswith((".jpg", ".png", ".gif")):
                            url = entity[i]["url"]
                    elif type == "url":
                        offset = entity[i]["offset"]
                        length = entity[i]["length"]
                        link = update.message.reply_to_message.text[offset:length+offset]
                        if link.endswith((".jpg", ".png", ".gif")):
                            url = link
                r = requests.get(url)
                with open(dl_path + "original.jpg", "wb") as f:
                    f.write(r.content)
            # Document
            elif update.message.reply_to_message.document is not None:
                if update.message.reply_to_message.document.file_name.endswith((".jpg", ".png")):
                    document = update.message.reply_to_message.document.file_id
                    bot.getFile(document).download(dl_path + "original.jpg")
                else:
                    raise Exception("Not a valid image")
            # Sticker
            elif update.message.reply_to_message.sticker is not None:
                sticker = update.message.reply_to_message.sticker.file_id
                bot.getFile(sticker).download(dl_path + "original.png")
                stick = "convert  " + dl_path + "original.png -background white -flatten " + dl_path + "original.jpg"
                subprocess.run(stick, shell=True)
            # Photo in reply
            elif update.message.reply_to_message.photo is not None:
                photo = update.message.reply_to_message.photo[-1].file_id
                bot.getFile(photo).download(dl_path + "original.jpg")
    # Photo w/ caption
    else:
        photo = update.message.photo[-1].file_id
        bot.getFile(photo).download(dl_path + "original.jpg")
