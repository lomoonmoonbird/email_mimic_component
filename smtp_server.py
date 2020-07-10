#! --*-- coding: utf-8 --*--
from proxies import smtp_core
from proxies.smtp_proxy import SMTPProxy, readConfig

if __name__ == '__main__':
    try:
        readConfig()
        s = smtp_core.SMTPServer(9000)
        s.serve(impl_class=SMTPProxy)
    except:
        import traceback
        traceback.print_exc()
        pass
