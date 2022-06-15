import os

from benedict import benedict

methods = ['ntfy', 'Telegram']


class Configs:
    cfgpath = ''
    cfg = None
    lastnotifid = -1

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
            self.cfg = benedict({'all': {'method': methods[0], 'interval': 5}, methods[0]: {'key': ''}, methods[1]: {'key': '', 'chatid': ''}})
            self.update()
        else:
            self.cfg = benedict.from_ini(self.cfgpath)
        file.close()

    def update(self):
        self.cfg.to_ini(filepath=self.cfgpath)
