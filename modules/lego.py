import legofy, datetime, requests, re, yaml

#import paths
with open('config.yml', 'r') as f:
    lego_folder = yaml.load(f)["path"]["lego"]

def lego(bot, update):
    #check reply
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
                    bot.sendMessage(chat_id=update.message.chat_id, text="Paremeter needs to be a number!", reply_to_message_id=update.message.message_id)
                    return
                if size > 100:
                    bot.sendMessage(chat_id=update.message.chat_id, text="Baka, make it from 1 to 100!", reply_to_message_id=update.message.message_id)
                    return
            # if replied message had a link, download image
            try:
                if "http:" in update.message.reply_to_message.text:
                    url = re.findall('http[s]?://\S+?\.(?:jpg|jpeg|png|gif)', update.message.reply_to_message.text)
                    link = str(url)
                    print(link[2:-2])
                    with open(lego_folder+"original.jpg", "wb") as code:
                        code.write(r.content)
                # if not, download photo from replied message
                else:
                    bot.getFile(update.message.reply_to_message.photo[-1].file_id).download(lego_folder+"original.jpg")
                legofy.main(image_path=lego_folder+"original.jpg", output_path=lego_folder+"legofied.jpg", size=size, palette_mode=None, dither=False)
                with open(lego_folder+"legofied.jpg", "rb") as f:
                    bot.sendPhoto(update.message.chat_id, f, reply_to_message_id=update.message.message_id)
                print(datetime.datetime.now(), ">>>", "Done legofying", ">>>", update.message.from_user.username)
            except:
                bot.sendMessage(update.message.chat_id, text="I can't get the image!", reply_to_message_id=update.message.message_id)
    
    #check message with photo and caption
    elif "/lego" in update.message.caption:
        parts = update.message.caption.split(" ", 1)
        if len(parts) == 1:
            size = 60
        else:
            try:
                size = int(parts[1])
            except:
                bot.sendMessage(chat_id=update.message.chat_id, text="Paremeter needs to be a number!", reply_to_message_id=update.message.message_id)
                return
            if size > 100:
                bot.sendMessage(chat_id=update.message.chat_id, text="Baka, make it from 1 to 100!", reply_to_message_id=update.message.message_id)
                return
        bot.getFile(update.message.photo[-1].file_id).download(lego_folder+"original.jpg")
        legofy.main(image_path=lego_folder+"original.jpg", output_path="lego/legofied.jpg", size=size, palette_mode=None, dither=False)
        with open(lego_folder+"legofied.jpg", "rb") as f:
            bot.sendPhoto(update.message.chat_id, f, reply_to_message_id=update.message.message_id)
        print(datetime.datetime.now(), ">>>", "Done legofying", ">>>", update.message.from_user.username)