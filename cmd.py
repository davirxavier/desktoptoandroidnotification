import asyncio
import sys
import threading
import senders
import signal

import configs

args = sys.argv[1:]


def startLoop():
    configs.task = configs.loop.create_task(configs.listener.startListening())
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    try:
        threading.Thread(target=lambda: configs.loop.run_until_complete(configs.task)).start()
    except asyncio.CancelledError:
        pass


def start():
    method = args[0]
    if method == configs.methods[0]:
        configs.cfg.method = configs.methods[0]
        if configs.cfg.key and len(configs.cfg.key) > 0:
            startLoop()
        else:
            print('Invalid ntfy room key, set in the cfg.ini file.')
            exit()

    elif method == configs.methods[1].lower():
        configs.cfg.method = configs.methods[1]

        if configs.cfg.key and len(configs.cfg.key) > 0 and configs.cfg.chatid:
            senders.instBot(lambda: print('Telegram bot key is invalid!'))
            startLoop()
        else:
            print('Invalid telegram bot key and chatid, set in the cfg.ini file.')
            exit()
    else:
        print('Invalid method, specify between: ' + str(configs.methods))
        exit()