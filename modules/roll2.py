def roll2(bot, update):
    from random import randint
    import datetime
    or_word_ru = " или "
    or_word_en = " or "
    if or_word_ru in update.message.text:
        text_roll2 = ''.join(update.message.text)
        split_text = text_roll2.split(or_word_ru)
        randoms = len(split_text) - 1
        answer = randint(0, randoms)
        uncapitalized = split_text[answer]
        for i, c in enumerate(uncapitalized):
            if not c.isdigit():
                break
        capitalized = uncapitalized[:i] + uncapitalized[i:].capitalize()
        bot.sendMessage(chat_id=update.message.chat_id, text=capitalized, reply_to_message_id=update.message.message_id)
        print(datetime.datetime.now(), ">>>", "Done advanced rolling", ">>>", update.message.from_user.username)
    elif or_word_en in update.message.text:
        text_roll2 = ''.join(update.message.text)
        split_text = text_roll2.split(or_word_en)
        randoms = len(split_text) - 1
        answer = randint(0, randoms)
        uncapitalized = split_text[answer]
        for i, c in enumerate(uncapitalized):
            if not c.isdigit():
                break
        capitalized = uncapitalized[:i] + uncapitalized[i:].capitalize()
        bot.sendMessage(chat_id=update.message.chat_id, text=capitalized, reply_to_message_id=update.message.message_id)
        print(datetime.datetime.now(), ">>>", "Done advanced rolling", ">>>", update.message.from_user.username)
    