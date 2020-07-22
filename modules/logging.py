#!/usr/bin/python
# -*- coding: utf-8 -*-
from datetime import datetime
import threading
import sqlite3
import time


def logging_decorator(command_name):
    def decorator(func):
        def wrapper(update, context, *args, **kwargs):
            time1 = time.time()
            current_time = datetime.strftime(datetime.now(), "%d.%m.%Y %H:%M:%S")
            data = func(update, context, *args, **kwargs)
            time2 = time.time()
            print(
                "{} > /{} > {} > {} > {} > {:.0f} ms".format(
                    current_time,
                    command_name,
                    update.message.from_user.username,
                    update.message.from_user.id,
                    data,
                    (time2-time1)*1000
                )
            )
            log_command(update, context, current_time, command_name)
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


def get_chat_info(update, context):
    user_name = update.effective_message.from_user.name
    if user_name.startswith("@"):
        user_name = user_name[1:]
    chat_id = update.effective_message.chat_id
    user_id = update.effective_message.from_user.id
    chat = context.bot.getChat(chat_id)
    return chat_id, chat.title, user_id, user_name


def log_command(update, context, date, command):
    table_name = "commands"
    entry_columns = "date, user_id, user, command, chat_id, chat_title" 
    chat_id, chat_title, user_id, user = get_chat_info(update, context)
    values = [date, user_id, user, command, chat_id, chat_title]
    data_entry(table_name, entry_columns, values)
