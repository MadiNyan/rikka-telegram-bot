#!/usr/bin/python
# -*- coding: utf-8 -*-
from datetime import datetime
import threading
import sqlite3
import time


def logging_decorator(command_name):
    def decorator(func):
        def wrapper(update, context, *args, **kwargs):
            if not update.message:
                return
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
        return wrapper
    return decorator


def module_init(gd):
    pass
