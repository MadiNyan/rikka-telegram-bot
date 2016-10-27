import legofy
import datetime
import requests
import re
import yaml

# import paths
with open('config.yml', 'r') as f:
    lego_folder = yaml.load(f)["path"]["lego"]


def lego(bot, update):
    # check reply
    if update.message.reply_to_message is not None:
        # check if command used on reply
        if "/lego" in update.message.text:
            parts = update.message.text.split(" ", 1)
            if len(parts) == 1:
                size = 60
            else:
                try:
                    size = int(parts[1])
                except:
                    update.message.reply_text("Paremeter needs to be a number!")
                    return
                if size > 100:
                    update.message.reply_text("Baka, make it from 1 to 100!")
                    return
            # if replied message had a link, download image
            try:
                if "http" in update.message.reply_to_message.text:
                    url = re.findall('http[s]?://\S+?\.(?:jpg|jpeg|png|gif)', update.message.reply_to_message.text)
                    link = str(url)
                    r = requests.get(link[2:-2])
                    with open(lego_folder+"original.jpg", "wb") as code:
                        code.write(r.content)
                # if not, download photo from replied message
                else:
                    bot.getFile(update.message.reply_to_message.photo[-1].file_id).download(lego_folder+"original.jpg")
                legofy.main(image_path=lego_folder+"original.jpg",
                            output_path=lego_folder+"legofied.jpg",
                            size=size, palette_mode=None, dither=False)
                with open(lego_folder+"legofied.jpg", "rb") as f:
                    update.message.reply_photo(f)
                print(datetime.datetime.now(), ">>>", "Done legofying", ">>>", update.message.from_user.username)
            except:
                update.message.reply_text("I can't get the image!")

    # check message with photo and caption
    elif "/lego" in update.message.caption:
        parts = update.message.caption.split(" ", 1)
        if len(parts) == 1:
            size = 60
        else:
            try:
                size = int(parts[1])
            except:
                update.message.reply_text("Paremeter needs to be a number!")
                return
            if size > 100:
                update.message.reply_text("Baka, make it from 1 to 100!")
                return
        bot.getFile(update.message.photo[-1].file_id).download(lego_folder+"original.jpg")
        legofy.main(image_path=lego_folder+"original.jpg",
                    output_path=lego_folder+"legofied.jpg",
                    size=size, palette_mode=None, dither=False)
        with open(lego_folder+"legofied.jpg", "rb") as f:
            update.message.reply_photo(f)
        print(datetime.datetime.now(), ">>>", "Done legofying", ">>>", update.message.from_user.username)
