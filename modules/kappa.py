import datetime
kappas = ["kappa", "каппа"]


def kappa(bot, update):
    for word in kappas:
        if word in update.message.text.lower():
            with open("resources/kappa.webp", "rb") as kappa:
                bot.sendSticker(update.message.chat_id, kappa, reply_to_message_id=update.message.message_id)
            print(datetime.datetime.now(), ">>>", "Kappa", ">>>", update.message.from_user.username)
            break
