from telegram.ext import MessageHandler, Filters
import datetime

def handler(dp):
    dp.add_handler(MessageHandler(Filters.text, kappa))

kappas = ["kappa", "каппа"]


def kappa(bot, update):
    for word in kappas:
        if word in update.message.text.lower():
            with open("resources/kappa.webp", "rb") as kappa:
                update.message.reply_sticker(kappa)
            print(datetime.datetime.now(), ">>>", "Kappa", ">>>", update.message.from_user.username)
            break
