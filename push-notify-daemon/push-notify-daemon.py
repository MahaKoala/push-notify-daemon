#!/usr/bin/python3
from optparse import OptionParser
import subprocess
import threading
import socket
import json
import os

from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GObject
import dbus

APPNAME = "com.vhakulinen.push-notification"
INVOKED = "ActionInvoked"

BROWSER = "firefox"
TIMEOUT = 5
BUFSIZE = 1024

BINDFILE = "/tmp/notification-socket"

notification = None
url = ""
# Dirty hack around for multi triggered event problem
count = 0


class Receiver(threading.Thread):
    running = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM, 0)

        if os.path.exists(BINDFILE):
            os.remove(BINDFILE)
        self.sock.bind(BINDFILE)

    def run(self):
        self.running = True
        self.sock.listen(1)
        while self.running:
            try:
                conn, _ = self.sock.accept()
            except:
                continue
            raw = conn.recv(BUFSIZE)
            conn.close()

            data = ""
            data = json.loads(raw.decode("UTF-8"))
            if data and validate(data):
                notify(data)

    def join(self, *args, **kwargs):
        self.running = False
        self.sock.shutdown(socket.SHUT_RDWR)
        if os.path.exists(BINDFILE):
            os.remove(BINDFILE)
        return super().join(*args, **kwargs)


def validate(data):
    return all(i in data for i in ["Title", "Body", "Url"])


def notify(data):
    global url
    global count
    url = data["Url"]

    # Add actions
    notification.connect_to_signal(INVOKED, action_callback)
    notification.connect_to_signal('NotificationClosed', closed_callback)

    # Call the methods and print the results
    notification.Notify(APPNAME, 0, "what", data["Title"],
                        data["Body"], [INVOKED, "Open URL"], "", TIMEOUT)
    count += 1


def action_callback(*args, **kwargs):
    global count
    for i in args:
        if i == INVOKED and count > 0:
            count -= 1
            subprocess.call(["%s %s &" % (BROWSER, url)], shell=True)


def closed_callback(*args, **kwargs):
    pass


if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-b", "--browser", help="Browser command to execute",
                      default="firefox", dest="browser")
    parser.add_option("-t", "--timeout", help="Timeout in seconds", default=5,
                      dest="timeout")

    (options, args) = parser.parse_args()

    BROWSER = options.browser
    TIMEOUT = options.timeout

    # Get mainloop
    loop = GObject.MainLoop()
    # Get dbus loop
    bus_loop = DBusGMainLoop()
    # Get the session bus
    bus = dbus.SessionBus(mainloop=bus_loop)

    # Get the interface
    notification = dbus.Interface(
        bus.get_object('org.freedesktop.Notifications',
                       '/org/freedesktop/Notifications'),
        'org.freedesktop.Notifications')

    receiver = Receiver()
    receiver.start()

    try:
        loop.run()
    except:
        pass
    receiver.join()
