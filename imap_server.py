#! --*-- coding: utf-8 --*--
from proxies import imap_core

if __name__ == '__main__':
    try:
        s = imap_core.IMAPServer(7000)
        s.serve()
    except:
        import traceback
        traceback.print_exc()
        pass
