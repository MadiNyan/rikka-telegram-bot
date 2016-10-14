import modules.instagram_filters, inspect, yaml, datetime, requests, re
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

#import paths
with open('config.yml', 'r') as f:
    path = yaml.load(f)["path"]["instagram"]

filters = []
all_funcs = inspect.getmembers(modules.instagram_filters, inspect.isfunction)
for i in range (0, len(all_funcs)):
    if all_funcs[i][0].startswith("filt_"):
        filters.append(all_funcs[i][0])

def instagram(bot, update):
    if "/instagram" in update.message.text:
        if update.message.reply_to_message is not None:
            try:
                if "http:" in update.message.reply_to_message.text:
                    url = re.findall('http[s]?://\S+?\.(?:jpg|jpeg|png|gif)', update.message.reply_to_message.text)
                    link = str(url)
                    r = requests.get(link[2:-2])
                    with open(path+"original.jpg", "wb") as code:
                        code.write(r.content)
                else:
                    bot.getFile(update.message.reply_to_message.photo[-1].file_id).download(path+"original.jpg")
            except:
                bot.sendMessage(update.message.chat_id, text="I can't get the image! :c", reply_to_message_id=update.message.message_id)
                return
        else:
            bot.sendMessage(update.message.chat_id, text="You need an image for that ^_^", reply_to_message_id=update.message.message_id)
            return
    elif "/instagram" in update.message.caption:
        bot.getFile(update.message.photo[-1].file_id).download(path+"original.jpg")
    instagram_key_list = []
    for i in filters:
        instagram_key = InlineKeyboardButton(str(i)[5:], callback_data=i)
        instagram_key_list.append(instagram_key)
    row_split = lambda list, size, acc=[]: row_split(list[size:], size, acc+[(list[:size])]) if list else acc
    rows = row_split(instagram_key_list, 3)
    instagram_keyboard = rows
    instagram_reply_markup = InlineKeyboardMarkup(instagram_keyboard)
    update.message.reply_text('Available filters are:', reply_markup=instagram_reply_markup)

def instagram_button(bot, update):
    instagram_query = update.callback_query
    filter = update.callback_query.data
    filter_name = str(filter)[5:]
    bot.editMessageText(text="Selected filter: %s\nProcessing..." % filter_name,
                        chat_id=instagram_query.message.chat_id,
                        message_id=instagram_query.message.message_id)
    try:
        getattr(modules.instagram_filters, filter)(path)
    except:
        print("Instagram error")
    with open(path+filter_name+".jpg", "rb") as f:
        bot.sendPhoto(instagram_query.message.chat_id, f)
    print(datetime.datetime.now(), ">>>", "Sent instagram photo", ">>>", instagram_query.message.from_user.username)
