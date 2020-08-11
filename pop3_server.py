#! --*-- coding: utf-8 --*--
from proxies import pop_core, pop_core_old

if __name__ == '__main__':
    try:
        s = pop_core.POPServer(8000)
        # s = pop_core_old.POPServer(8000)
        s.serve()
    except:
        import traceback
        traceback.print_exc()
        pass
