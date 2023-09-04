#! --*-- coding: utf-8 --*--
from proxies import right_smtp_core, right_smtp_proxy
from proxies.right_smtp_proxy import SMTPProxy
from proxies.config import readConfig
import threading

if __name__ == '__main__':
    try:
        t = threading.Thread(target=right_smtp_proxy.SMTPProxy().handle_schedule_mails, args=())
        t.start()
        smtpcfg = readConfig("proxies/right_internal_smtp_config.ini")
        s = right_smtp_core.SMTPServer(smtpcfg['config'].port)
        s.serve(impl_class=SMTPProxy)
    except:
        import traceback
        traceback.print_exc()
        pass
