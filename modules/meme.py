import datetime, requests, re
from modules.memegenerator import make_meme
def meme(bot, update):
    if "/meme" in update.message.caption:
        initial_text = "".join(update.message.caption[6:]).upper()
        meme_splitter = "@"
        bot.getFile(update.message.photo[-1].file_id).download("memes/original.jpg")
        if meme_splitter in update.message.caption:
            split_text = initial_text.split(meme_splitter)
            make_meme(split_text[0], split_text[1], "memes/original.jpg")
        else:
            split_text = initial_text
            make_meme("", split_text, "memes/original.jpg")
        with open("memes/meme.jpg", "rb") as meme:
            bot.sendPhoto(update.message.chat_id, meme, reply_to_message_id=update.message.message_id)
            print(datetime.datetime.now(), ">>>", "Done /meme", ">>>", update.message.from_user.username)
    elif update.message.reply_to_message is not None:
        if "/meme" in update.message.text:
            try:
                if "http" in update.message.reply_to_message.text:
                    url = re.findall('http[s]?://\S+?\.(?:jpg|jpeg|png|gif)', update.message.reply_to_message.text)
                    link = str(url)
                    r = requests.get(link[2:-2])
                    with open("memes/original.jpg", "wb") as code:
                        code.write(r.content)
                else:
                    bot.getFile(update.message.reply_to_message.photo[-1].file_id).download("memes/original.jpg")
                initial_text = "".join(update.message.text[6:]).upper()
                meme_splitter = "@"
                if meme_splitter in update.message.text:
                    split_text = initial_text.split(meme_splitter)
                    make_meme(split_text[0], split_text[1], "memes/original.jpg")
                else:
                    split_text = initial_text
                    make_meme("", split_text, "memes/original.jpg")
                with open("memes/meme.jpg", "rb") as meme:
                    bot.sendPhoto(update.message.chat_id, meme, reply_to_message_id=update.message.message_id)
                    print(datetime.datetime.now(), ">>>", "Done /meme", ">>>", update.message.from_user.username)
            except: 
                bot.sendMessage(update.message.chat_id, text="I can't get the image!", reply_to_message_id=update.message.message_id)