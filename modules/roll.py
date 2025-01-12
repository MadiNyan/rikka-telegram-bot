from random import randint

from telegram import Update
from telegram.ext import PrefixHandler

from modules.logging import logging_decorator


def module_init(gd):
    commands = gd.config["commands"]
    for command in commands:
        gd.application.add_handler(PrefixHandler("/", command, roll))


@logging_decorator("roll")
async def roll(update: Update, context):
    """Roll a dice with a specified number of sides. Accepts both '20' and 'd20' formats."""
    if update.message is None:
        return

    # Default to d20
    sides = 20

    if context.args:
        try:
            # Remove 'd' or 'D' prefix if present
            arg = context.args[0].lower().strip('d')
            sides = int(arg)
            if sides < 1:
                await update.message.reply_text("Number of sides must be positive")
                return
        except ValueError:
            await update.message.reply_text("Please provide a valid number (e.g., '20' or 'd20')")
            return

    # Roll the dice
    result = randint(1, sides)
    await update.message.reply_text(f"(d{sides}) 🎲 {result}")