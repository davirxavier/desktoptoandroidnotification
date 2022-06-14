from gui import sg
import asyncio
from typing import Callable
from configs import cfg, methodsFn
import configs
import winsdk.windows.networking.connectivity
from winsdk.windows.foundation.metadata import ApiInformation
from winsdk.windows.ui.notifications.management import UserNotificationListener, UserNotificationListenerAccessStatus
from winsdk.windows.ui.notifications import NotificationKinds, KnownNotificationBindings


def getcomputername():
    hostnames = winsdk.windows.networking.connectivity.NetworkInformation.get_host_names().first()
    if hostnames.has_current:
        return hostnames.current.display_name
    else:
        return 'Unknown Device'


async def startListening(onStopped: Callable = lambda: False):
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


def stopListening(onStopped: Callable = lambda: False):
    if configs.task:
        configs.task.cancel()
    # onStopped()


def treatNotifTextElements(notif, appinfo):
    elements = []
    for curr in notif:
        elements.append(curr.text)

    title = elements[0]
    text = ''
    if len(elements) > 1:
        text = '\n'.join(elements[1:])

    methodsFn[cfg.method](title, text, appinfo)


def onNotification(toasts):
    for toast in toasts:
        treatNotifTextElements(toast.notification.visual.get_binding(KnownNotificationBindings.get_toast_generic()).get_text_elements(), toast.app_info.display_info.display_name)