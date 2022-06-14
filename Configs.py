import os

from benedict import benedict

methods = ['ntfy', 'Telegram']


class Configs:
    cfgpath = ''
    cfg = None
    lastnotifid = -1

    @property
    def roomkey(self):
        return self.cfg['ntfy.key']

    @roomkey.setter
    def roomkey(self, value):
        self.cfg['ntfy.key'] = value
        self.update()

    @property
    def method(self):
        return self.cfg['all.method']

    @method.setter
    def method(self, value):
        self.cfg['all.method'] = value
        self.update()

    def __init__(self, cfgpath='cfg.ini'):
        self.cfgpath = cfgpath
        file = open('cfg.ini', 'a+')
        if os.stat(cfgpath).st_size < 15:
            self.cfg = benedict({'all': {'method': methods[0]}, methods[0]: {'key': ''}, methods[1]: {}})
            self.update()
        else:
            self.cfg = benedict.from_ini(self.cfgpath)
        file.close()

    def update(self):
        self.cfg.to_ini(filepath=self.cfgpath)
