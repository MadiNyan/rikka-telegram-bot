
from random import randint, seed

from telegram import Update
from telegram.ext import PrefixHandler

from modules.logging import logging_decorator

choices = ["It is certain", "It is decidedly so", "Without a doubt", "Yes definitely",
           "You may rely on it", "As I see it, yes", "Most likely", "Outlook good",
           "Yes", "Signs point to yes", "Reply hazy try again", "Ask again later",
           "Better not tell you now", "Cannot predict now", "Concentrate and ask again",
           "Don't count on it", "My reply is no", "My sources say no", "Outlook not so good",
           "Very doubtful"]

splitter_ru = " или "
splitter_en = " or "
splitters = [" or ", " или "]


def module_init(gd):
    commands = gd.config["commands"]
    for command in commands:
        gd.application.add_handler(PrefixHandler("/", command, roll))


async def mysteryball(update, string):
    seed() if string == "" else seed(string)
    answer = randint(0, len(choices)-1)
    await update.message.reply_text("🎱 " + choices[answer])


def splitter_check(text):
    for splitter in splitters:
        if splitter in text:
            return splitter


async def rolling_process(update, full_text, split_text):
    seed(full_text)
    randoms = len(split_text) - 1
    answer = randint(0, randoms)
    uncapitalized = split_text[answer]
    capitalized = uncapitalized[0].upper() + uncapitalized[1:]
    await update.message.reply_text("⚖️ " + capitalized)


def numbers_check(text):
    try:
        rng_end = int(text)
        return 0, rng_end
    except ValueError:
        pass
    if "-" in text:
        numbers = text.split("-")
        try:
            rng_start = int(numbers[0])
            rng_end = int(numbers[1])
            return rng_start, rng_end
        except:
            return None, None
    else:
        return None, None


async def dice(update, number1, number2):
    if number1 is not None and number2 is not None:
        if number1 > number2:
            tmp = number1
            number1 = number2
            number2 = tmp
        random_number = randint(number1, number2)
        await update.message.reply_text("🎲 " + str(random_number))
        return True


@logging_decorator("roll")
async def roll(update: Update, context):
    if update.message is None: return
    args = context.args
    if update.message.reply_to_message is not None:
        args = update.message.reply_to_message.text.split(" ")
        if args[0].startswith("/"):
            args.pop(0)
    full_text = ' '.join(args)
    rng_start, rng_end = numbers_check(full_text)
    if await dice(update, rng_start, rng_end):
        return
    splitter = splitter_check(full_text)
    if splitter:
        split_text = full_text.split(splitter)
        await rolling_process(update, full_text, split_text)
    else:
        await mysteryball(update, full_text)
