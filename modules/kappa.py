import datetime
def kappa(bot, update):
    if "kappa" or "Kappa" or "Каппа" or "каппа" in update.message.text:
        with open("resources/kappa.webp", "rb") as kappa:
            bot.sendSticker(update.message.chat_id, kappa, reply_to_message_id=update.message.message_id)

    print(datetime.datetime.now(), ">>>", "Kappa", ">>>", update.message.from_user.username)