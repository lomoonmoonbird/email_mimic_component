#! --*-- coding: utf-8 --*--
from proxies import smtp_core
from proxies.smtp_proxy import SMTPProxy
from proxies.config import readConfig
from proxies.utils import Logging

if __name__ == '__main__':
    try:
        smtpcfg = readConfig("proxies/smtp_config.ini")
        s = smtp_core.SMTPServer(smtpcfg['config'].port, Logging())
        s.serve(impl_class=SMTPProxy)
    except:
        import traceback
        traceback.print_exc()
        pass
