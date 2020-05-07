![Rikka Bot Logo](https://madi.cat/trash/rikka-bot.png)

*My personal multipurpose chat bot with completely random features*  
*Can be found at [@Rikka_Bot](https://telegram.me/Rikka_Bot)*

![Python ver](http://img.shields.io/badge/Python-3.6-yellow.svg) 
[![Build Status](https://scrutinizer-ci.com/g/MadiNyan/rikka-telegram-bot/badges/build.png?b=master)](https://scrutinizer-ci.com/g/MadiNyan/rikka-telegram-bot/build-status/master) 
[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/MadiNyan/rikka-telegram-bot/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/MadiNyan/rikka-telegram-bot/?branch=master) 
[![Code Climate](https://codeclimate.com/github/MadiNyan/rikka-telegram-bot/badges/gpa.svg)](https://codeclimate.com/github/MadiNyan/rikka-telegram-bot) 
[![Contact Me](https://img.shields.io/badge/Contact-Me-blue.svg)](https://telegram.me/Madi_Nyan) 

----------

## Requirements:
+ Python 3.6+
+ ImageMagick 7.0.10+

### Libraries:
See requirements.txt

## How to
Run `update_deps.bat` to automatically install `requirements.txt` libraries
Configure your token, api keys, commands, extensions and paths for each module in config.yml
```
keys:
     telegram_token: =====key=====

features:
    gif:
        enabled: true
        commands: 
            - gif
        path: userdata/mp4/

    glitch:
        enabled: true
        commands: 
            - glitch
        path: userdata/glitch/
        extensions:
            - .jpg
            - .jpeg
            - .png
            - .bmp 
            - .webp

    google_search:
        enabled: true
        commands_image: 
            - img
        google_dev_key: =====key=====
        google_cse_id: =====key=====
```

## Available functions:
+ /a [tag] - get pic from yande.re
+ /activity - most active bot users
+ /colors [from 1 to 10] - generate image palette with given number of colors
+ /gif - get random gif, "/gif help" to see folders
+ /glitch - glitch an image
+ /img - Google image search
+ /jpeg [from 1 to 10] - compress image
+ /kek [-l, -r, -t, -b] - mirror one side of an image to another
+ /leet - convert text to 1337 5P34K
+ /lego [from 1 to 100] - legofy image
+ /liq [from 1 to 100] - liquid rescale image
+ /meme [-c, -i, -l] [top text] @ [bottom text] - make a meme from image
+ /nya - get random asian girl pic
+ /rate - rate stuff
+ /roll - fortune tell
+ /roll [1] or [2] - choose one option randomly
+ /roll [X-Y] - returns random number between X and Y
+ /say - Text-to-Speech
+ /server - show server cpu, ram, hdd load and uptime
+ /start - start a bot or view welcome message
+ /usage [all|local] - bot usage graph
+ /zalgo - z̡͛a͖̅l̡ͨg̦͊o͍͛ text generator
