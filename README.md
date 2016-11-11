![Rikka Bot Logo](http://madi.so/rikka-bot.png)

*My personal multipurpose chat bot with completely random features*  
*Can be found at [@Rikka_Bot](https://telegram.me/Rikka_Bot)*

![Python ver](http://img.shields.io/badge/Python-3.5-yellow.svg) [![Build Status](https://scrutinizer-ci.com/g/MadiNyan/rikka-telegram-bot/badges/build.png?b=master)](https://scrutinizer-ci.com/g/MadiNyan/rikka-telegram-bot/build-status/master) [![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/MadiNyan/rikka-telegram-bot/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/MadiNyan/rikka-telegram-bot/?branch=external-img-dl) [![Code Climate](https://codeclimate.com/github/MadiNyan/rikka-telegram-bot/badges/gpa.svg)](https://codeclimate.com/github/MadiNyan/rikka-telegram-bot) [![Contact Me](https://img.shields.io/badge/Contact-Me-blue.svg)](https://telegram.me/Madi_Nyan) 

----------

## Requirements:
+ Python 3.5
+ ImageMagick

### Libraries:
+ [python-telegram-bot](https://github.com/python-telegram-bot)
+ [py-bing-search](https://github.com/tristantao/py-bing-search)
+ [legofy](https://github.com/JuanPotato/Legofy)
+ [PyBooru](https://github.com/LuqueDaniel/pybooru)
+ Pillow
+ psutil
+ requests
+ uptime

## How to
Configure your token, api key and paths in config.yml (without any quotations), and don't forget the font
```
    keys:
        telegram_token: 123455
        bing_api_key: 123456

    path:
        gifs: examples/gifs/
        memes: examples/memes/
        meme_font: resources/font_name.ttf
        glitch: examples/glitch/
        lego: examples/lego/
        nya: examples/nya/
        kek: examples/kek/
        instagram: examples/instagram/
        anime: examples/
        liquid: examples/liquid
```

## Available functions:
+ /start - start a bot or view welcome message
+ /leet - convert text to 1337 5P34K
+ /roll [1] or [2] - choose one option randomly
+ /toribash [username] - show Toribash stats
+ /glitch - glitch an image
+ /lego [from 1 to 100] - legofy image
+ /gif - get random gif, "/gif help" to see folders
+ /nya - get random asian girl pic
+ /meme [top text] @ [bottom text] - make a meme from image
+ /kek [-l, -r, -t, -b] - mirror one side of an image to another
+ /liq [from 1 to 100] - liquid rescale image
+ /instagram or /ig - add filter to an image
+ /img, /vid, /news [query] - Bing search for random result
+ /a [tag] - get pic from yande.re
+ /status - show server cpu, ram, hdd load and uptime
