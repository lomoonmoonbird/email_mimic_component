from configparser import ConfigParser, RawConfigParser

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