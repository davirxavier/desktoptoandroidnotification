from sys import platform
import configs
import gui
import cmd
import sys

print('Starting...')

if platform == "linux" or platform == "linux2":
    print('Linux detected, using dbus listener.')
    import listeners.dbuslistener as dbusl
    configs.listener = dbusl
elif platform == "win32":
    print('Windows detected, using winsdk listener.')
    import listeners.winlistener as winlistener
    configs.listener = winlistener

print('Acquiring computer name...')
configs.cfg.computername = configs.listener.getcomputername()

args = sys.argv[1:]

if len(args) > 0:
    print('Detected commandline args, starting without gui.')
    cmd.start()
else:
    print('No commandline args, starting with gui.')
    gui.start()

print('Started.')


