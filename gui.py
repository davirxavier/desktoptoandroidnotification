import threading
import PySimpleGUI as sg
import senders
import asyncio
import webbrowser

from configs import cfg, methods, loop
import configs

methodsDesc = {
    methods[0]: 'Input your ntfy theme name below:',
    methods[1]: 'Input your telegram bot apikey and desired chat id below:'
}

asyncio.set_event_loop(loop)
stopping = False
stopApp = False
listening = False

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


def change_method():
    global window
    window['startbtn'].update('Start listening')
    configs.listener.stopListening(lambda: onStopped())
    window['secretkey'].update(cfg.key)
    window['methoddesc'].update(methodsDesc[cfg.method])
    window['chatid'].update(visible=cfg.method == methods[1])
    window['generaterandombtn'].update(visible=cfg.method == methods[0])


def start():
    global stopping, listening, stopApp

    while True:
        event, values = window.read()

        if event == 'intervalcombo':
            cfg.interval = values['intervalcombo']

        if event == 'generaterandombtn':
            key = senders.ntfyIdGenerator()
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
                    senders.instBot(lambda: sg.Popup('Invalid api key.', keep_on_top=True))

                window['startbtn'].update('Stop listening')
                configs.task = loop.create_task(configs.listener.startListening(lambda: onStopped()))
                window['secretkey'].update(disabled=True)
                window['changedmethod'].update(disabled=True)
                window['intervalcombo'].update(disabled=True)
                window['chatid'].update(disabled=True)

                try:
                    threading.Thread(target=lambda: loop.run_until_complete(configs.task)).start()
                except asyncio.CancelledError:
                    pass
            else:
                window['startbtn'].update(disabled=True)
                stopping = True
                configs.listener.stopListening(lambda: onStopped())

        if event == sg.WIN_CLOSED:
            stopping = True
            stopApp = True
            configs.listener.stopListening(lambda: onStopped())
            break

        if event == 'learnmorelink':
            webbrowser.open('https://github.com/davirxavier/windowstoandroidnotification')