#!/usr/bin/python
# -*- coding: utf-8 -*-
from telegram.ext import MessageHandler, Filters
from datetime import datetime, timedelta
import sqlite3


def module_init(gd):
    global c, conn
    path = gd.config["path"]
    conn  = sqlite3.connect(path+"rikka.db", check_same_thread=False) 
    c = conn.cursor()
    gd.dp.add_handler(MessageHandler(Filters.all, get_chats), group=1)
    #gd.dp.add_handler(MessageHandler(Filters.all, get_chat_info), group=2)


def create_table(name, columns):
    c.execute("CREATE TABLE IF NOT EXISTS "+name+"("+columns+")")
    conn.commit()


def data_entry(table, entry_columns, values):
    values_count = ("?, "*len(values))[:-2]
    c.execute("INSERT INTO "+table+" ("+entry_columns+") VALUES ("+values_count+")", (values))
    conn.commit()


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
            c.execute("DELETE FROM "+table+" WHERE chat_id = %s" %(row))
            conn.commit()


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
    if chat.type == "private":
        owner = user_name
    else:
        admins = chat.get_administrators(CREATOR = "creator")
        for admin in admins:
            if admin.status == "creator":
                owner = admin.user.username
    return chat_id, chat.type, chat.title, chat.username, chat.description, chat.get_members_count(), owner, user_id, user_name


def get_chats(bot, update):
    get_message(bot, update)
    current_time = datetime.strftime(datetime.now(), "%d.%m.%Y %H:%M:%S")
    current_time_obj = datetime.strptime(current_time, "%d.%m.%Y %H:%M:%S")
    table_name = "chats"
    creation_columns = "date TEXT, chat_id INTEGER, chat_type TEXT, chat_title TEXT, chat_username TEXT, chat_desc TEXT, chat_members INTEGER, owner TEXT"
    entry_columns = "date, chat_id, chat_type, chat_title, chat_username, chat_desc, chat_members, owner" 
    create_table(table_name, creation_columns)
    delete_old(table_name, current_time_obj)
    chat_id, chat_type, chat_title, chat_username, chat_desc, chat_members, owner, _, user = get_chat_info(bot, update)
    if check_entry(chat_id, table_name):
        return
    values = [current_time, chat_id, chat_type, chat_title, chat_username, chat_desc, chat_members, owner]
    data_entry(table_name, entry_columns, values)


def log_command(bot, update, date, command):
    table_name = "commands"
    creation_columns = "date TEXT, user_id INTEGER, user TEXT, command TEXT, chat_id INTEGER, chat_title TEXT"
    entry_columns = "date, user_id, user, command, chat_id, chat_title" 
    create_table(table_name, creation_columns)
    ci = get_chat_info(bot, update)
    chat_id, chat_title, user_id, user = ci[0], ci[2], ci[7], ci[8]
    values = [date, user_id, user, command, chat_id, chat_title]
    data_entry(table_name, entry_columns, values)


def get_message(bot, update):
    current_time = datetime.strftime(datetime.now(), "%d.%m.%Y %H:%M:%S")
    table_name = "messages"
    creation_columns = "date TEXT, chat_id INTEGER, chat_type TEXT, chat_title TEXT, user_id INTEGER, user TEXT, message TEXT, photo BLOB"
    entry_columns = "date, chat_id, chat_type, chat_title, user_id, user, message, photo" 
    create_table(table_name, creation_columns)
    ci = get_chat_info(bot, update)
    chat_id, chat_type, chat_title, user_id, user = ci[0], ci[1], ci[2], ci[7], ci[8]
    message = update.message.text
    try:
        img = bot.getFile(update.message.photo[-1].file_id)["file_path"]
    except:
        img = None
    values = [current_time, chat_id, chat_type, chat_title, user_id, user, message, img]
    data_entry(table_name, entry_columns, values)