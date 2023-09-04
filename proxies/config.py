#! --*-- coding:utf-8 --*--

from configparser import ConfigParser, RawConfigParser
import os
from collections import defaultdict
from itertools import count

try:
    from configparser import OrderedDict as _default_dict
except ImportError:
    # fallback for setup.py which hasn't yet built _collections
    _default_dict = dict

class Config(RawConfigParser ):
    def __init__(self, defaults=None, dict_type=_default_dict,
                 allow_no_value=False):
        super().__init__(defaults, dict_type, allow_no_value)

    def get(self, section, option, default=None, **kwargs):

        res = default
        if super().has_option(section, option):
            res = super().get(section, option)
        return res

    def getboolean(self, section, option, default=None, **kwargs):

        res = default
        if ConfigParser.has_option(self, section, option):
            res = super().getboolean(section, option)
        return res

    def getint(self, section, option, default=None, **kwargs):

        res = default
        if super().has_option(section, option):
            res = super().getint(section, option)
        return res

    def getlist(self, section, option, default=None):

        res = default
        if super().has_option(section, option):
            res = super().get(section, option).strip()
            res = res.replace('\n', ' ')
            if ' ' in res:
                res = res.split(' ')
            else:
                res = [res]
            while '' in res:
                res.remove('')
        return res

class _config(object):

    def __init__(self, name):
        self.name = name
        self.age = 1

    def __repr__(self):
        return "Var(%s) age(%s)" % (self.name, self.age)


class smtpconfig(defaultdict):

    def __init__(self, *args, **kwargs):
        super(smtpconfig, self).__init__(_config, *args, **kwargs)

    def __missing__(self, key, unique=count()):
        if self.default_factory is None:
            raise KeyError(key)
        if key == "_":
            return self.default_factory(key + str(next(unique)))
        self[key] = value = self.default_factory(key)
        return value

def readConfig(config_path=""):
    """读取配置"""
    configFile = config_path
    if os.path.exists(configFile) == False:
        print('Configuration file "' + configFile + '" doesn''t exist. Exiting.')
        return False

    cfg =Config()
    cfg.read([configFile])
    smtpcfg = smtpconfig()
    smtpcfg['config'].port = cfg.getint('config', 'port', 25)
    smtpcfg['config'].debuglevel = cfg.getint('config', 'port', 5)
    smtpcfg['config'].distribute_hosts = cfg.get('config', 'distribute_hosts', '[]')
    smtpcfg['config'].redis_server = cfg.get('config', 'redis_server', '')
    smtpcfg['config'].redis_port = cfg.get('config', 'redis_port', 6379)
    smtpcfg['config'].redis_db = cfg.get('config', 'redis_db', 0)

    return smtpcfg