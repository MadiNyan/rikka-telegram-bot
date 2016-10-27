def roll(bot, update, args):
    from random import randint
    import datetime
    text_roll = ' '.join(args)
    splitter_ru = " или "
    splitter_en = " or "
    if splitter_ru in text_roll:
        split_text = text_roll.split(splitter_ru)
        randoms = len(split_text) - 1
        answer = randint(0, randoms)
        uncapitalized = split_text[answer]
        for i, c in enumerate(uncapitalized):
            if not c.isdigit():
                break
        capitalized = uncapitalized[:i] + uncapitalized[i:].capitalize()
        update.message.reply_text(capitalized)
    elif splitter_en in text_roll:
        split_text = text_roll.split(splitter_en)
        randoms = len(split_text) - 1
        answer = randint(0, randoms)
        uncapitalized = split_text[answer]
        for i, c in enumerate(uncapitalized):
            if not c.isdigit():
                break
        capitalized = uncapitalized[:i] + uncapitalized[i:].capitalize()
        update.message.reply_text(capitalized)
    print(datetime.datetime.now(), ">>>", "Done /roll", ">>>", update.message.from_user.username)
