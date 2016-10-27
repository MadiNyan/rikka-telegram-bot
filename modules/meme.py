import datetime
import requests
import re
import yaml
from modules.memegenerator import make_meme

# import paths
with open("config.yml", "r") as f:
    memes_folder = yaml.load(f)["path"]["memes"]


def meme(bot, update):
    if "/meme" in update.message.caption:
        initial_text = "".join(update.message.caption[6:]).upper()
        meme_splitter = "@"
        bot.getFile(update.message.photo[-1].file_id).download(memes_folder+"original.jpg")
        if meme_splitter in update.message.caption:
            split_text = initial_text.split(meme_splitter)
            make_meme(split_text[0], split_text[1], memes_folder+"original.jpg")
        else:
            split_text = initial_text
            make_meme("", split_text, memes_folder+"original.jpg")
        with open(memes_folder+"meme.jpg", "rb") as f:
            update.message.reply_photo(f)
            print(datetime.datetime.now(), ">>>", "Done /meme", ">>>", update.message.from_user.username)
    elif update.message.reply_to_message is not None:
        if "/meme" in update.message.text:
            try:
                if "http" in update.message.reply_to_message.text:
                    url = re.findall("http[s]?://\S+?\.(?:jpg|jpeg|png|gif)", update.message.reply_to_message.text)
                    link = str(url)
                    r = requests.get(link[2:-2])
                    with open(memes_folder+"original.jpg", "wb") as code:
                        code.write(r.content)
                else:
                    bot.getFile(update.message.reply_to_message.photo[-1].file_id).download(memes_folder+"original.jpg")
                initial_text = "".join(update.message.text[6:]).upper()
                meme_splitter = "@"
                if meme_splitter in update.message.text:
                    split_text = initial_text.split(meme_splitter)
                    make_meme(split_text[0], split_text[1], memes_folder+"original.jpg")
                else:
                    split_text = initial_text
                    make_meme("", split_text, memes_folder+"original.jpg")
                with open(memes_folder+"meme.jpg", "rb") as f:
                    update.message.reply_photo(f)
                    print(datetime.datetime.now(), ">>>", "Done /meme", ">>>", update.message.from_user.username)
            except:
                update.message.reply_text("I can't get the image!")
