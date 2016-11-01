from telegram import ChatAction
import requests
import datetime


def toristats(bot, update, args):
    update.message.chat.send_action(ChatAction.TYPING)
    user = args[0]
    toristats = "http://forum.toribash.com/tori_stats.php?format=json"
    full_link = toristats + "&username=" + user
    r = requests.get(full_link)
    json = r.json()

    userid = json["userid"]
    username = json["username"]
    qi = json["qi"]
    belt = json["belt"]
    clanname = json["clanname"]
    elo = json["elo"]
    winratio = json["winratio"]
    tc = json["tc"]
    lastact = str(datetime.datetime.fromtimestamp(int(json["lastactivity"])))

    output = ("User ID: " + userid + "\nUsername: " + username +
              "\nQi: " + str(qi) + ", " + belt +
              "\nClan: " + clanname +
              "\nWin Ratio: " + str(winratio)[:-2] + "%, " + str(elo)[:-4] + " elo" +
              "\nToricredits: " + str(tc)) + "\nLast Active: " + lastact
    update.message.reply_text(output)
    print(datetime.datetime.now(), ">>>", "Done /toribash", ">>>", update.message.from_user.username)
