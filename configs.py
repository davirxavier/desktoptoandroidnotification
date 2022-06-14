import os
import asyncio
import senders

from benedict import benedict

methods = ['ntfy', 'Telegram']
configVersion = 1
loop = asyncio.new_event_loop()
task = None
bot = None
listener = None

methodsFn = {
    methods[0]: lambda title, text, appinfo='Unknown Application': senders.sendNtfy(title, text, appinfo),
    methods[1]: lambda title, text, appinfo='Unknown Application': senders.sendTelegram(title, text, appinfo)
}


class Configs:
    cfgpath = ''
    cfg = None
    lastnotifid = -1
    computername = 'Unknown Device'

    @property
    def key(self):
        return self.cfg[self.method + '.key']

    @key.setter
    def key(self, value):
        self.cfg[self.method + '.key'] = value
        self.update()

    @property
    def method(self):
        return self.cfg['all.method']

    @method.setter
    def method(self, value):
        self.cfg['all.method'] = value
        self.update()

    @property
    def interval(self):
        return self.cfg['all.interval']

    @interval.setter
    def interval(self, value):
        self.cfg['all.interval'] = value
        self.update()

    @property
    def chatid(self):
        return self.cfg[methods[1] + '.chatid']

    @chatid.setter
    def chatid(self, value):
        self.cfg[methods[1] + '.chatid'] = value
        self.update()

    def __init__(self, cfgpath='cfg.ini'):
        self.cfgpath = cfgpath
        file = open('cfg.ini', 'a+')
        if os.stat(cfgpath).st_size < 15:
            self.init_config_file()
        else:
            self.cfg = benedict.from_ini(self.cfgpath)
            if configVersion > self.cfg.get_int('all.version', -1):
                self.init_config_file()
        file.close()

    def init_config_file(self):
        self.cfg = benedict(
            {'all': {'method': methods[0], 'interval': 5, 'version': configVersion}, methods[0]: {'key': ''},
             methods[1]: {'key': '', 'chatid': ''}})
        self.update()

    def update(self):
        self.cfg.to_ini(filepath=self.cfgpath)


cfg = Configs()
senders.cfg = cfg
