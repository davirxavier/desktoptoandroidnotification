from typing import Callable

import requests
import telegram
import random
import string

bot = None
cfg = None


def instBot(errorCallback: Callable = lambda: False):
    global bot
    try:
        bot = telegram.Bot(token=cfg.key)
    except telegram.error.InvalidToken:
        errorCallback()


def sendTelegram(title, text, appinfo='Unknown Application'):
    print('Sending notification with title ' + title + ' to telegram.')
    bot.send_message(chat_id=cfg.chatid, text='<i><b>' + title + '</b></i>\n\n' + text
                     + '\n\n<pre>' + cfg.computername + ' - ' + appinfo + '</pre>', parse_mode='html')


def ntfyIdGenerator(size=20, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.SystemRandom().choice(chars) for _ in range(size))


def sendNtfy(title, text, appinfo='Unknown Application'):
    print('Sending ntfy with title ' + title + ' to room ' + cfg.key + '.')
    requests.post("https://ntfy.sh/" + cfg.key,
                  data=text.encode(encoding='utf-8'),
                  headers={"Title": title.encode('utf-8'), "Tags": cfg.computername + ',' + appinfo})