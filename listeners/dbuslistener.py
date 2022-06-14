from typing import Callable

from configs import methodsFn, cfg
from gi.repository import GLib as glib
import dbus
from dbus.mainloop.glib import DBusGMainLoop
import socket

lastReplacesId = -1
notifKeys = ["app_name", "replaces_id", "app_icon", "summary",
             "body", "actions", "hints", "expire_timeout"]

loop = None

def dbus_notification(bus, message):
    global notifKeys

    args = message.get_args_list()
    if len(args) == 8:
        notification = dict([(notifKeys[i], args[i]) for i in range(8)])
        onNotification([notification])


def getcomputername():
    return socket.gethostname()


async def startListening():
    global loop

    DBusGMainLoop(set_as_default=True)
    session_bus = dbus.SessionBus()
    session_bus.add_match_string(
        "type='method_call',interface='org.freedesktop.Notifications',member='Notify',eavesdrop=true")
    session_bus.add_message_filter(dbus_notification)
    loop = glib.MainLoop()
    loop.run()


def stopListening(onStopped: Callable = lambda: False):
    loop.quit()
    onStopped()


def onNotification(toasts):
    global lastReplacesId

    notif = toasts[0]
    if notif["replaces_id"] != lastReplacesId:
        lastReplacesId = notif["replaces_id"]
        methodsFn[cfg.method](notif["summary"], notif["body"], notif["app_name"])
