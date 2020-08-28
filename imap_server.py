#! --*-- coding: utf-8 --*--
from proxies import imap_core_multi
from proxies import imap_core_single
from proxies.imap_proxy_bak import IMAP_Proxy
# from proxies.imap_proxy import IMAP_Proxy
if __name__ == '__main__':
    try:
        s = imap_core_multi.IMAPServer(7000)
        s.serve()
        # IMAP_Proxy(7000, verbose=False)
    except:
        import traceback
        traceback.print_exc()
        pass
