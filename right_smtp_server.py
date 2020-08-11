#! --*-- coding: utf-8 --*--
from proxies import right_smtp_core
from proxies.right_smtp_proxy import SMTPProxy
from proxies.config import readConfig

if __name__ == '__main__':
    try:
        smtpcfg = readConfig("proxies/right_smtp_config.ini")
        s = right_smtp_core.SMTPServer(smtpcfg['config'].port)
        s.serve(impl_class=SMTPProxy)
    except:
        import traceback
        traceback.print_exc()
        pass
