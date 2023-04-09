import asyncio
from datetime import datetime


def logging_decorator(command_name):
    def decorator(func):
        async def wrapper(update, context, *args, **kwargs):
            if update.message is None:
                return
            time1 = asyncio.get_event_loop().time()
            current_time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
            data = await func(update, context, *args, **kwargs)
            time2 = asyncio.get_event_loop().time()
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
