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


def create_table(name, columns):
    c.execute("CREATE TABLE IF NOT EXISTS "+name+"("+columns+")")


def data_entry(table, entry_columns, values):
    values_count = ("?, "*len(values))[:-2]
    c.execute("INSERT INTO "+table+" ("+entry_columns+") VALUES ("+values_count+")", (values))
    conn.commit()


def check_entry(chat_id, table):
    c.execute("SELECT chat_id FROM "+table)
    for row in c.fetchall():
        if chat_id in row:
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


def get_chats(bot, update):
    current_time = datetime.strftime(datetime.now(), "%d.%m.%Y %H:%M:%S")
    current_time_obj = datetime.strptime(current_time, "%d.%m.%Y %H:%M:%S")
    table_name = "chats"
    creation_columns = "date TEXT, chat_id INTEGER, chat_type TEXT, chat_title TEXT, chat_username TEXT, chat_desc TEXT, chat_members INTEGER, owner TEXT"
    entry_columns = "date, chat_id, chat_type, chat_title, chat_username, chat_desc, chat_members, owner" 
    create_table(table_name, creation_columns)
    delete_old(table_name, current_time_obj)

    chat_id = update.effective_message.chat_id
    if check_entry(chat_id, table_name):
        return
    chat = bot.getChat(chat_id)
    chat_type = chat.type
    chat_title = chat.title
    chat_username = chat.username
    chat_desc = chat.description
    chat_members = chat.get_members_count()
    if chat_type == "private":
        owner = update.effective_message.from_user.name
        if owner.startswith("@"):
            owner = owner[1:]
    else:
        admins = chat.get_administrators(CREATOR = "creator")
        for admin in admins:
            if admin.status == "creator":
                owner = admin.user.username
    values = [current_time, chat_id, chat_type, chat_title, chat_username, chat_desc, chat_members, owner]
    data_entry(table_name, entry_columns, values)


def log_command(update, date, command):
    table_name = "commands"
    creation_columns = "date TEXT, user TEXT, command TEXT, chat_id INTEGER, chat_title TEXT"
    entry_columns = "date, user, command, chat_id, chat_title" 
    create_table(table_name, creation_columns)
    if update.callback_query is not None:
        user = update.callback_query.message.chat.username
    else:
        user = update.effective_message.from_user.name[1:]
    chat_id = update.effective_message.chat_id
    chat_title = update.effective_message.chat.title

    values = [date, user, command, chat_id, chat_title]
    data_entry(table_name, entry_columns, values)
