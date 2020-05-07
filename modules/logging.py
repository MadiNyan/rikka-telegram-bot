#!/usr/bin/python
# -*- coding: utf-8 -*-
from telegram.ext import CommandHandler
from datetime import datetime
import threading
import sqlite3


def logging_decorator(command_name):
    def decorator(func):
        def wrapper(bot, update, *args, **kwargs):
            current_time = datetime.strftime(datetime.now(), "%d.%m.%Y %H:%M:%S")
            data = func(bot, update, *args, **kwargs)
            print(
                "{} > /{} > {} > {} > {}".format(
                    current_time,
                    command_name,
                    update.message.from_user.username,
                    update.message.from_user.id,
                    data
                )
            )
            log_command(bot, update, current_time, command_name)
        return wrapper
    return decorator


def module_init(gd):
    global c, conn, db_lock
    db_lock = threading.Lock()
    path = gd.config["path"]
    conn  = sqlite3.connect(path+"rikka.db", check_same_thread=False)
    c = conn.cursor()


def data_entry(table, entry_columns, values):
    values_count = ("?, "*len(values))[:-2]
    db_lock.acquire()
    c.execute("INSERT INTO "+table+" ("+entry_columns+") VALUES ("+values_count+")", (values))
    conn.commit()
    db_lock.release()


def check_entry(chat_id, table):
    c.execute("SELECT chat_id FROM "+table+" WHERE chat_id = %s" %(chat_id))
    if c.fetchone() is not None:
        return True
    else:
        return False


def get_chat_info(bot, update):
    if update.callback_query is not None:
        user_name = update.callback_query.message.chat.username
        chat_id = update.callback_query.message.chat_id
        user_id = update.callback_query.from_user.id
    else:
        user_name = update.effective_message.from_user.name[1:]
        chat_id = update.effective_message.chat_id
        user_id = update.effective_message.from_user.id
    chat = bot.getChat(chat_id)
    return chat_id, chat.title, user_id, user_name


def log_command(bot, update, date, command):
    table_name = "commands"
    entry_columns = "date, user_id, user, command, chat_id, chat_title" 
    chat_id, chat_title, user_id, user = get_chat_info(bot, update)
    values = [date, user_id, user, command, chat_id, chat_title]
    data_entry(table_name, entry_columns, values)
