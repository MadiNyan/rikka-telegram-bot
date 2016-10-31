from modules.get_image import get_image
import yaml
import subprocess
import datetime

# import path
with open("config.yml", "r") as f:
    kek_folder = yaml.load(f)["path"]["kek"]


# get image, pass parameter
def kek(bot, update):
    if update.message.reply_to_message is not None:
        kek_param = "".join(update.message.text[5:7])
    else:
        kek_param = "".join(update.message.caption[5:7])
    try:
        get_image(bot, update, kek_folder)
    except:
        update.message.reply_text("Can't get the image! :(")
        return
    result = kekify(bot, update, kek_param)
    try:
        with open(kek_folder+result, "rb") as f:
            update.message.reply_photo(f)
        print(datetime.datetime.now(), ">>>", "Done kek", ">>>", update.message.from_user.username)
    except:
        return


# kek process + send
def kekify(bot, update, kek_param):
    try:
        if kek_param == "-l" or kek_param == "":
            crop = "50%x100% "
            piece_one = "result-0.jpg "
            piece_two = "result-1.jpg "
            flip = "-flop "
            order = kek_folder + piece_one + kek_folder + piece_two
            append = "+append "
            result = "kek-left.jpg"
        elif kek_param == "-r":
            crop = "50%x100% "
            piece_one = "result-1.jpg "
            piece_two = "result-0.jpg "
            flip = "-flop "
            order = kek_folder + piece_two + kek_folder + piece_one
            append = "+append "
            result = "kek-right.jpg"
        elif kek_param == "-t":
            crop = "100%x50% "
            piece_one = "result-0.jpg "
            piece_two = "result-1.jpg "
            flip = "-flip "
            order = kek_folder + piece_one + kek_folder + piece_two
            append = "-append "
            result = "kek-top.jpg"
        elif kek_param == "-b":
            crop = "100%x50% "
            piece_one = "result-1.jpg "
            piece_two = "result-0.jpg "
            flip = "-flip "
            order = kek_folder + piece_two + kek_folder + piece_one
            append = "-append "
            result = "kek-bot.jpg"
        elif kek_param == "-m":
            kekify(bot, update, "-l")
            kekify(bot, update, "-r")
            kekify(bot, update, "-t")
            kekify(bot, update, "-b")
            append_lr = "convert " + kek_folder + "kek-left.jpg " + kek_folder + "kek-right.jpg +append " + kek_folder + "kek-lr-temp.jpg"
            subprocess.run(append_lr, shell=True)
            append_tb = "convert " + kek_folder + "kek-top.jpg " + kek_folder + "kek-bot.jpg +append " + kek_folder + "kek-tb-temp.jpg"
            subprocess.run(append_tb, shell=True)
            append_all = "convert " + kek_folder + "kek-lr-temp.jpg " + kek_folder + "kek-tb-temp.jpg -append " + kek_folder + "multikek.jpg"
            subprocess.run(append_all, shell=True)
            result = "multikek.jpg"
            return result
        cut = "convert " + kek_folder + "original.jpg -crop " + crop + kek_folder + "result.jpg"
        subprocess.run(cut, shell=True)
        mirror = "convert " + kek_folder + piece_one + flip + kek_folder + piece_two
        subprocess.run(mirror, shell=True)
        append = "convert " + order + append + kek_folder + result
        subprocess.run(append, shell=True)
        return result
    except:
        update.message.reply_text("Unknown kek parameter.\nUse -l, -r, -t, -b or -m")
