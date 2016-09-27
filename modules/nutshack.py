import datetime
from random import randint

def nutshack(bot, update):
    r = randint(1, 300)
    if r == 1:
        #bot.sendMessage(update.message.chat_id, text="It's the Nutshack!", reply_to_message_id=update.message.message_id)
        with open("resources/nutshack.mp3", "rb") as file:
            bot.sendVoice(update.message.chat_id, voice=file, reply_to_message_id=update.message.message_id)
        print(datetime.datetime.now(), ">>>", "It's the nutshack", ">>>", update.message.from_user.username)