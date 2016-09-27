def altcaps(bot, update, args):
    if update.message.reply_to_message is not None:
        args = update.message.reply_to_message.text
    ret = ""
    i = True  # capitalize first letter
    for i in range(0, len(args))
        if i == True:
            ret += char.upper()
            i = not i
        else:
            ret += char.lower()
    return ret
    print(ret)
    bot.sendMessage(chat_id=update.message.chat_id, text=ret, reply_to_message_id=update.message.message_id)
    print(datetime.datetime.now(), ">>>", "Done /altcaps", ">>>", update.message.from_user.username)