# rikka-telegram-bot
Multipurpose chat bot

## Requirements:
Python 3.5

### Libraries:
+ telegram
+ [python-telegram-bot](https://github.com/python-telegram-bot)
+ [py_bing_search](https://github.com/tristantao/py-bing-search)
+ [legofy](https://github.com/JuanPotato/Legofy)
+ PIL
+ psutil
+ requests
+ uptime

## How to
Put your bot token and Bing Api key in config.yml (without any quotations)
```
    keys:
     telegram_token: <here>
     bing_api_key: <and here>
```

## Available functions:
+ /start - start a bot or view welcome message
+ /caps - UPPER CASE your text
+ /leet - convert text to 1337 5P34K
+ /roll [1] or [2] - choose one option randomly
+ /toribash [username] - show Toribash stats
+ /glitch - break an image
+ /lego [from 1 to 100] - legofy image
+ /gif - get random gif, "/gif help" to see folders
+ /nya - get random girl pic
+ /meme [top text] @ [bottom text] - make a meme from image
+ /img, /vid, /news [query] - Bing search for random result
+ /status - show server cpu, ram, hdd load and uptime
