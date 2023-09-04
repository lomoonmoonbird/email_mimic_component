# -- * -- coding:utf-8 --*--


from proxies.http_proxy import HTTPServer
from proxies.config import readConfig

if __name__ == '__main__':
    httpcfg = readConfig("proxies/http_config.ini")
    try:
        s = HTTPServer().serve(port=httpcfg['config'].port)
        s.serve()
    except:
        import traceback
        traceback.print_exc()
        pass
