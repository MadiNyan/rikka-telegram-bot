import requests
import re


def get_image(bot, update, dl_path):
    if update.message.reply_to_message is not None:
        if "http" in update.message.reply_to_message.text:
                url = re.findall("http[s]?://\S+?\.(?:jpg|jpeg|png|gif|webp)", update.message.reply_to_message.text)
                r = requests.get(url[0])
                with open(dl_path + "original.jpg", "wb") as f:
                    f.write(r.content)
        elif update.message.reply_to_message.sticker is not None:
            sticker = update.message.reply_to_message.sticker.file_id
            bot.getFile(sticker).download(dl_path + "original.jpg")
        elif update.message.reply_to_message.document is not None:
            print(update.message.reply_to_message.document.file_name)
            if update.message.reply_to_message.document.file_name.endswith((".jpg", ".png")):
                document = update.message.reply_to_message.document.file_id
                bot.getFile(document).download(dl_path + "original.jpg")
            else:
                raise Exception("Not a valid image")
        else:
            photo = update.message.reply_to_message.photo[-1].file_id
            bot.getFile(photo).download(dl_path + "original.jpg")
    else:
        photo = update.message.photo[-1].file_id
        bot.getFile(photo).download(dl_path + "original.jpg")
