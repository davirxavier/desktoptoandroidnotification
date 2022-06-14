import asyncio
import threading

import requests
import PySimpleGUI as sg
from winsdk.windows.foundation.metadata import ApiInformation
from winsdk.windows.ui.notifications.management import UserNotificationListener, UserNotificationListenerAccessStatus
from winsdk.windows.ui.notifications import NotificationKinds, KnownNotificationBindings

from Configs import Configs, methods

cfg = Configs()
listening = False

methodsDesc = {
    methods[0]: 'Input your ntfy theme name below:',
    methods[1]: 'Input your telegram bot theme name below:'
}
methodsFn = {
    methods[0]: lambda title, text: sendNtfy(title, text),
    methods[1]: lambda title, text: sendTelegram(title, text)
}

stopping = False

def sendTelegram(title, text):
    pass

def sendNtfy(title, text):
    print('Sending ntfy with title ' + title + ' to room ' + cfg.roomkey + '.')
    requests.post("https://ntfy.sh/" + cfg.roomkey,
                  data=text.encode(encoding='utf-8'),
                  headers={ "Title": title.encode('utf-8') })

async def startListening():
    if not ApiInformation.is_type_present("Windows.UI.Notifications.Management.UserNotificationListener"):
        print("UserNotificationListener is not supported on this device.")
        exit()

    listener = UserNotificationListener.get_current()
    accessStatus = await listener.request_access_async()

    while True:
        if accessStatus != UserNotificationListenerAccessStatus.ALLOWED:
            print("Access to UserNotificationListener is not allowed.")
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
            await asyncio.sleep(10)
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
    window['startbtn'].update('Start listening', disabled=False)
    window['secretkey'].update(disabled=False)
    window['changedmethod'].update(disabled=False)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
task = None

sg.theme("DarkBlue")
layout = [
    [
        sg.Text("Select your desired notification method:"),
    ],
    [
        sg.Combo(methods, default_value=cfg.method, readonly=True, size=(15, 1), enable_events=True, key='changedmethod'),
        sg.Text("Learn more...", enable_events=True, font=('Arial', 8, 'underline'))
    ],
    [
        sg.Text("Input your ntfy theme name below:", key='methoddesc'),
    ], [
        sg.In(size=(29, 1), key='secretkey', default_text=cfg.roomkey)
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

    if event == 'changedmethod':
        cfg.method = values['changedmethod']
        stopListening()
        window['startbtn'].update('Start listening')
        window['secretkey'].update('')
        window['methoddesc'].update(methodsDesc[cfg.method])

    if event == 'startbtn' and not stopping:
        cfg.roomkey = values['secretkey']
        listening = not listening
        if listening:
            window['startbtn'].update('Stop listening')
            task = loop.create_task(startListening())
            window['secretkey'].update(disabled=True)
            window['changedmethod'].update(disabled=True)

            try:
                threading.Thread(target=lambda: loop.run_until_complete(task)).start()
            except asyncio.CancelledError:
                pass
        else:
            window['startbtn'].update(disabled=True)
            stopping = True
            stopListening()

    if event == sg.WIN_CLOSED:
        break

window.close()
loop.close()
