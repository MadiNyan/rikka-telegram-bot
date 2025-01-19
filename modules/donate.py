from datetime import datetime, timedelta
import sqlite3
import threading
import os
from telegram import Update, LabeledPrice
from telegram.ext import (
    MessageHandler, 
    PrefixHandler, 
    ContextTypes, 
    CallbackContext, 
    PreCheckoutQueryHandler,
    filters
)
from telegram.error import BadRequest

from modules.logging import logging_decorator

# Thread-local storage for database connections
local = threading.local()


def get_db():
    if not hasattr(local, "db"):
        # Create userdata directory if it doesn't exist
        os.makedirs("userdata", exist_ok=True)
        
        # Connect to database
        local.db = sqlite3.connect("userdata/donate.db")
        
        # Create table if it doesn't exist
        with local.db:
            local.db.execute("""
                CREATE TABLE IF NOT EXISTS donations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    user_id INTEGER NOT NULL,
                    username TEXT NOT NULL,
                    stars INTEGER NOT NULL,
                    transaction_id TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'success'
                )
            """)
    return local.db

def module_init(gd):
    global contact, admin_id, amount
    contact = gd.config["contact"]
    commands = gd.config["commands"]
    admin_id = gd.full_config["admin_id"]
    amount = gd.config["amount"]
    gd.application.add_handler(PrefixHandler("/", commands, donate))
    gd.application.add_handler(PrefixHandler("/", "paysupport", paysupport))
    gd.application.add_handler(PrefixHandler("/", "refund", refund))
    gd.application.add_handler(PrefixHandler("/", "manualrefund", manualrefund))
    gd.application.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    gd.application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback))


@logging_decorator("donate")
async def donate(update: Update, context:ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    # Define a title, description, and prices for the donation
    title = "Support Rikka Bot"
    description = "Your support helps improve and maintain the bot. Thank you!"
    payload = "rikka_donation_payload"  # Custom payload identifier
    currency = "XTR"  # XTR for TG stars
    prices = [LabeledPrice(f"{amount} Stars", amount)]

    # Send an invoice
    await context.bot.send_invoice(
        chat_id=chat_id,
        title=title,
        description=description,
        payload=payload,
        provider_token="",
        currency=currency,
        prices=prices,
        start_parameter=None,
    )


async def precheckout_callback(update: Update, context: CallbackContext):
    #Handle pre-checkout queries
    query = update.pre_checkout_query

    # Answer the pre-checkout query (approve or decline the payment)
    if query.invoice_payload != "donation_payload":
        await query.answer(ok=False, error_message="Something went wrong. Please try again.")
    else:
        await query.answer(ok=True)


async def successful_payment_callback(update: Update, context: CallbackContext):
    #Handle successful payments
    payment = update.message.successful_payment
    user_id = update.effective_user.id
    username = update.effective_user.username or str(user_id)
    date = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    stars = payment.total_amount  # Amount in stars
    transaction_id = payment.telegram_payment_charge_id

    # Store payment information in database
    db = get_db()
    with db:
        db.execute(
            "INSERT INTO donations (date, user_id, username, stars, transaction_id, status) VALUES (?, ?, ?, ?, ?, ?)",
            (date, user_id, username, stars, transaction_id, "success")
        )

    await update.message.reply_text("Thank you for your donation! ⭐")


async def paysupport(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Please use /refund to request a refund for your last payment.\n"
        "Note: you can only refund payments made in the last 24 hours\n\n"
        "If you have any questions, please contact " + contact + ".\n"
        "Thank you for your support!"
        )


@logging_decorator("refund")
async def refund(update: Update, context: CallbackContext):
    #Handle refund requests
    user_id = update.effective_user.id
    
    try:
        # Get the most recent non-refunded transaction for this user from last 24 hours
        db = get_db()
        current_time = datetime.now()
        time_24h_ago = (current_time - timedelta(hours=24)).strftime("%d.%m.%Y %H:%M:%S")
        
        with db:
            cursor = db.execute(
                """
                SELECT transaction_id, id, date 
                FROM donations 
                WHERE user_id = ? 
                AND status = 'success' 
                AND date > ?
                ORDER BY id DESC 
                LIMIT 1
                """,
                (user_id, time_24h_ago)
            )
            result = cursor.fetchone()
            
        if not result:
            raise BadRequest("No eligible payments found for refund. Note: you can only refund payments made in the last 24 hours")
            
        transaction_id, donation_id, payment_date = result
        
        # Try to refund the payment
        result = await context.bot.refund_star_payment(
            user_id=user_id,
            telegram_payment_charge_id=transaction_id
        )
        
        if result:
            # Update the status to refunded in the database
            with db:
                db.execute(
                    "UPDATE donations SET status = 'refunded' WHERE id = ?",
                    (donation_id,)
                )
            
            await update.message.reply_text(
                "✅ Your refund request has been processed successfully.\n"
                "The stars will be returned to your account shortly."
            )
        else:
            raise BadRequest("Unable to process refund")
            
    except BadRequest as e:
        # Send message with support information if refund fails
        await update.message.reply_text(
            "⚠️ Unable to process automatic refund:\n" + str(e) + "\n\n"
            "Please contact " + contact + " with the following information:\n"
            "1. Your Transaction ID (if available)\n"
            "2. Date and timeof payment\n"
            "3. Reason for refund\n\n"
            "I will assist you as soon as possible.",
        )

@logging_decorator("manualrefund")
async def manualrefund(update: Update, context: CallbackContext):
    if update.effective_user.id not in admin_id:
        await update.message.reply_text("You are not authorized to use this command.")
        return
    
    try:    
        user_id = context.args[0]
        transaction_id = context.args[1]

        result = await context.bot.refund_star_payment(
            user_id=user_id,
            telegram_payment_charge_id=transaction_id
        )

        if result: 
            await update.message.reply_text(
                "✅ Successfully refunded stars."
            )
        else:
            raise BadRequest("Unable to process refund")
    except BadRequest as e:
        await update.message.reply_text("Error: " + str(e))
