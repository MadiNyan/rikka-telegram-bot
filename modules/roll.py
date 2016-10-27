from random import randint
import datetime


def roll(bot, update, args):
    text_roll = ' '.join(args)
    splitter_ru = " или "
    splitter_en = " or "
    if splitter_ru in text_roll:
        split_text = text_roll.split(splitter_ru)
    elif splitter_en in text_roll:
        split_text = text_roll.split(splitter_en)
    rolling_process(update, split_text)

def rolling_process(update, split_text):
    randoms = len(split_text) - 1
    answer = randint(0, randoms)
    uncapitalized = split_text[answer]
    for i, c in enumerate(uncapitalized):
        if not c.isdigit():
            break
    capitalized = uncapitalized[:i] + uncapitalized[i:].capitalize()
    update.message.reply_text(capitalized)
    print(datetime.datetime.now(), ">>>", "Done /roll", ">>>", update.message.from_user.username)
