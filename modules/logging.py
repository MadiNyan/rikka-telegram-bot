#!/usr/bin/python
# -*- coding: utf-8 -*-
from telegram.ext import MessageHandler, Filters
from datetime import datetime, timedelta
import threading
import sqlite3


def module_init(gd):
    global c, conn, db_lock
    db_lock = threading.Lock()
    path = gd.config["path"]
    conn  = sqlite3.connect(path+"rikka.db", check_same_thread=False) 
    c = conn.cursor()
    gd.dp.add_handler(MessageHandler(Filters.all, get_chats), group=1)


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


def delete_old(table, date):
    span = timedelta(days=7)
    c.execute("SELECT chat_id FROM "+table)
    for row in c.fetchall():
        c.execute("SELECT date FROM "+table+" WHERE chat_id = %s" %(row))
        old_date = c.fetchone()[0]
        old_date_time = datetime.strptime(old_date, "%d.%m.%Y %H:%M:%S")
        if date - old_date_time > span:
            db_lock.acquire()
            c.execute("DELETE FROM "+table+" WHERE chat_id = %s" %(row))
            conn.commit()
            db_lock.release()


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
    owner = None
    if chat.type == "private":
        owner = user_name
    else:
        admins = chat.get_administrators(CREATOR = "creator")
        for admin in admins:
            if admin.status == "creator":
                owner = admin.user.username
    return chat_id, chat.type, chat.title, chat.username, chat.description, chat.get_members_count(), owner, user_id, user_name


def get_chats(bot, update):
    current_time = datetime.strftime(datetime.now(), "%d.%m.%Y %H:%M:%S")
    current_time_obj = datetime.strptime(current_time, "%d.%m.%Y %H:%M:%S")
    table_name = "chats"
    entry_columns = "date, chat_id, chat_type, chat_title, chat_username, chat_desc, chat_members, owner" 
    delete_old(table_name, current_time_obj)
    chat_id, chat_type, chat_title, chat_username, chat_desc, chat_members, owner, _, _ = get_chat_info(bot, update)
    if check_entry(chat_id, table_name):
        return
    values = [current_time, chat_id, chat_type, chat_title, chat_username, chat_desc, chat_members, owner]
    data_entry(table_name, entry_columns, values)


def log_command(bot, update, date, command):
    table_name = "commands"
    entry_columns = "date, user_id, user, command, chat_id, chat_title" 
    ci = get_chat_info(bot, update)
    chat_id, chat_title, user_id, user = ci[0], ci[2], ci[7], ci[8]
    values = [date, user_id, user, command, chat_id, chat_title]
    data_entry(table_name, entry_columns, values)


def vk(bot, update):
    current_time = datetime.strftime(datetime.now(), "%d.%m.%Y %H:%M:%S")
    table_name = "vk"
    entry_columns = "date, unixtime, post_id"
    values = [0, 0, 0]
    c.execute("SELECT unixtime FROM vk ORDER BY rowid DESC LIMIT 1")
    fetch = c.fetchone()
    if fetch is not None:
        old_date = int(fetch[0])
        return current_time, old_date
    else:
        data_entry(table_name, entry_columns, values)
        return current_time, 0

def vk_add(bot, update, date, unixtime, post_id):
    table_name = "vk"
    entry_columns = "date, unixtime, post_id"
    values = [date, unixtime, post_id]
    data_entry(table_name, entry_columns, values)
