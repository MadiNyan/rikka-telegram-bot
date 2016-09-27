import datetime
def caps(bot, update, args):
    if update.message.reply_to_message is not None:
        args = update.message.reply_to_message.text
        args = args.split(" ")
        text_caps = ''.join(args).upper()
    text_caps = ' '.join(args).upper()
    bot.sendMessage(chat_id=update.message.chat_id, text=text_caps, reply_to_message_id=update.message.message_id)
    print(datetime.datetime.now(), ">>>", "Done /caps", ">>>", update.message.from_user.username)