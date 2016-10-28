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
    kekify(bot, update, kek_param)


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
        elif kek_param == "-r":
            crop = "50%x100% "
            piece_one = "result-1.jpg "
            piece_two = "result-0.jpg "
            flip = "-flop "
            order = kek_folder + piece_two + kek_folder + piece_one
            append = "+append "
        elif kek_param == "-t":
            crop = "100%x50% "
            piece_one = "result-0.jpg "
            piece_two = "result-1.jpg "
            flip = "-flip "
            order = kek_folder + piece_one + kek_folder + piece_two
            append = "-append "
        elif kek_param == "-b":
            crop = "100%x50% "
            piece_one = "result-1.jpg "
            piece_two = "result-0.jpg "
            flip = "-flip "
            order = kek_folder + piece_two + kek_folder + piece_one
            append = "-append "
        cut = "convert " + kek_folder + "original.jpg -crop " + crop + kek_folder + "result.jpg"
        subprocess.run(cut, shell=True)
        mirror = "convert " + kek_folder + piece_one + flip + kek_folder + piece_two
        subprocess.run(mirror, shell=True)
        append = "convert " + order + append + kek_folder + "kek.jpg"
        subprocess.run(append, shell=True)
        with open(kek_folder+"kek.jpg", "rb") as f:
            update.message.reply_photo(f)
        print(datetime.datetime.now(), ">>>", "Done kek", ">>>", update.message.from_user.username)
    except:
        update.message.reply_text("Unknown kek parameter.\nUse -l, -r, -t or -b")
