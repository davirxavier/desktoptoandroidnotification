import asyncio
import random
import string
import threading

import webbrowser
import requests
import telegram
import PySimpleGUI as sg
from winsdk.windows.foundation.metadata import ApiInformation
from winsdk.windows.ui.notifications.management import UserNotificationListener, UserNotificationListenerAccessStatus
from winsdk.windows.ui.notifications import NotificationKinds, KnownNotificationBindings

from Configs import Configs, methods

cfg = Configs()
listening = False

methodsDesc = {
    methods[0]: 'Input your ntfy theme name below:',
    methods[1]: 'Input your telegram bot apikey and desired chat id below:'
}
methodsFn = {
    methods[0]: lambda title, text: sendNtfy(title, text),
    methods[1]: lambda title, text: sendTelegram(title, text)
}

stopping = False
stopApp = False

bot = None

def sendTelegram(title, text):
    print('Sending notification with title ' + title + ' to telegram.')
    bot.send_message(chat_id=cfg.chatid, text='<i><b>' + title + '</b></i>\n\n' + text, parse_mode='html')


def sendNtfy(title, text):
    print('Sending ntfy with title ' + title + ' to room ' + cfg.key + '.')
    requests.post("https://ntfy.sh/" + cfg.key,
                  data=text.encode(encoding='utf-8'),
                  headers={"Title": title.encode('utf-8')})


async def startListening():
    global window

    if not ApiInformation.is_type_present("Windows.UI.Notifications.Management.UserNotificationListener"):
        print("UserNotificationListener is not supported on this device.")
        sg.Popup('UserNotificationListener is not supported on this device.', keep_on_top=True)
        exit()

    listener = UserNotificationListener.get_current()
    accessStatus = await listener.request_access_async()

    while True:
        if accessStatus != UserNotificationListenerAccessStatus.ALLOWED:
            print("Access to UserNotificationListener is not allowed.")
            sg.Popup('Access to UserNotificationListener is not allowed, the app may not work correctly.', keep_on_top=True)
            exit()

        print('Searching for new notifs...')
        notifs = await listener.get_notifications_async(NotificationKinds.TOAST)

        list = []
        for notif in notifs:
            list.append(notif)

        if cfg.lastnotifid == -1 and len(list) > 0:
            cfg.lastnotifid = list[-1].id

        list.sort(key=lambda e: e.id)
        lastNotif = 0
        for notif in list:
            if cfg.lastnotifid < notif.id:
                cfg.lastnotifid = notif.id
                break
            lastNotif = lastNotif + 1

        cfg.lastnotifid = list[-1].id
        list = list[lastNotif:]

        print('Found ' + str(len(list)) + ' new notifs, sending...')
        onNotification(list)
        try:
            await asyncio.sleep(cfg.interval)
        except asyncio.CancelledError:
            onStopped()
            break


def stopListening():
    if task:
        task.cancel()


def treatNotifTextElements(notif):
    elements = []
    for curr in notif:
        elements.append(curr.text)

    title = elements[0]
    if len(elements) > 1:
        text = '\n'.join(elements[1:])

    methodsFn[cfg.method](title, text)


def onNotification(toasts):
    for toast in toasts:
        treatNotifTextElements(toast.notification.visual.get_binding(KnownNotificationBindings.get_toast_generic()).get_text_elements())

def onStopped():
    global window, stopping
    stopping = False
    print('Stopped.')
    if stopApp:
        window.close()
        loop.close()
        exit()
        return
    window['startbtn'].update('Start listening', disabled=False)
    window['secretkey'].update(disabled=False)
    window['changedmethod'].update(disabled=False)
    window['intervalcombo'].update(disabled=False)
    window['chatid'].update(disabled=False)


def id_generator(size=20, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.SystemRandom().choice(chars) for _ in range(size))


def change_method():
    global window
    window['startbtn'].update('Start listening')
    stopListening()
    window['secretkey'].update(cfg.key)
    window['methoddesc'].update(methodsDesc[cfg.method])
    window['chatid'].update(visible=cfg.method == methods[1])
    window['generaterandombtn'].update(visible=cfg.method == methods[0])


loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
task = None

sg.theme("DarkBlue")
layout = [
    [
        sg.Text("Select your desired notification method:"),
    ],
    [
        sg.Combo(methods, default_value=cfg.method, readonly=True, size=(15, 1), enable_events=True,
                 key='changedmethod'),
        sg.Text("Learn more...", enable_events=True, font=('Arial', 8, 'underline'), key="learnmorelink")
    ],
    [
        sg.Text(methodsDesc[cfg.method], key='methoddesc'),
    ],
    [
        sg.In(size=(30, 1), key='secretkey', default_text=cfg.key),
        sg.Button("Generate random", key="generaterandombtn", visible=cfg.method == methods[0]),
        sg.In(size=(15, 1), default_text=cfg.chatid, key="chatid", visible=cfg.method == methods[1])
    ],
    [
        sg.Text("Refresh interval:"),
        sg.Combo([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20, 30, 60], default_value=cfg.interval, size=(15, 1), enable_events=True, key='intervalcombo')
    ],
    [
        sg.Button(button_text="Start listening", key="startbtn", pad=(0, 10))]
]
window = sg.Window(title="Win10NotificationSynchronizer",
                   layout=layout,
                   margins=(40, 30),
                   element_justification="center")

while True:
    event, values = window.read()

    if event == 'intervalcombo':
        cfg.interval = values['intervalcombo']

    if event == 'generaterandombtn':
        key = id_generator()
        window['secretkey'].update(key)
        cfg.key = key

    if event == 'changedmethod':
        cfg.method = values['changedmethod']
        change_method()

    if event == 'startbtn' and not stopping:
        cfg.key = values['secretkey']
        listening = not listening
        if listening:
            if cfg.method == methods[1]:
                cfg.chatid = values['chatid']
                try:
                    bot = telegram.Bot(token=cfg.key)
                except telegram.error.InvalidToken:
                    sg.Popup('Invalid api key.', keep_on_top=True)
                    listening = False
                    continue

            window['startbtn'].update('Stop listening')
            task = loop.create_task(startListening())
            window['secretkey'].update(disabled=True)
            window['changedmethod'].update(disabled=True)
            window['intervalcombo'].update(disabled=True)
            window['chatid'].update(disabled=True)

            try:
                threading.Thread(target=lambda: loop.run_until_complete(task)).start()
            except asyncio.CancelledError:
                pass
        else:
            window['startbtn'].update(disabled=True)
            stopping = True
            stopListening()

    if event == sg.WIN_CLOSED:
        stopping = True
        stopApp = True
        stopListening()
        break

    if event == 'learnmorelink':
        webbrowser.open('https://github.com/davirxavier/windowstoandroidnotification')