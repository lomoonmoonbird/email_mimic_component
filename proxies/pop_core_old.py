import socket, string, threading
import poplib

from proxies.config import readConfig

DEFAULT_KEY = "pop_proxy"
MAX_CLIENT = 10
CRLF = b'\r\n'
CONFIG_PATH = 'proxies/pop_config.ini'
smtpcfg = readConfig(CONFIG_PATH)

class Dispatch():

    @classmethod
    def dispatch(cls, cmd):
        return dict(
            USER=cls.handle_user,
            PASS=cls.handle_pass,
            STAT=cls.handle_stat,
            LIST=cls.handle_list,
            TOP=cls.handle_top,
            RETR=cls.handle_retr,
            DELE=cls.handle_dele,
            NOOP=cls.handle_noop,
            # SELECT=cls.handle_select,
            QUIT=cls.handle_quit,
            # LOGIN=cls.handle_login,
            # ID=cls.handle_id,
            # FETCH=cls.handle_fetch,
            # UIDL=cls.handle_uidl
        ).get(cmd)



    @classmethod
    def handle_user(cls, data):
        cls.username = 'jinpeng'
        return "+OK user accepted"

    @classmethod
    def handle_pass(cls, data):
        cls.password = 'jinpeng'
        return "+OK pass accepted"

    @classmethod
    def handle_stat(cls, data):
        return "+OK "

    @classmethod
    def handle_list(cls):
        return None

    @classmethod
    def handle_top(cls):
        return None

    @classmethod
    def handle_retr(cls, data):
        pass

    @classmethod
    def handle_dele(cls, data):
        return "+OK message 1 deleted"

    @classmethod
    def handle_noop(cls, data):
        return "+OK"

    @classmethod
    def handle_quit(cls, data):
        return "+OK proxy POP3 server signing off"

class POPServerEngine:
    """
    代理核心 实现smtp方法协议
    """



    def __init__(self, socket, log):
        self.socket = socket
        self.log = log

    def run(self):
        """
        运行引擎一直到退出命令
        """
        # self.socket.send(bytes("220 Python pop\r\n".encode()))
        self.socket.send(b"+OK proxy file-based pop3 server ready\r\n")

        while 1:
            try:
                data = b''
                complete_line = 0
                while not complete_line:
                    lump = self.socket.recv(1024)
                    if not isinstance(lump, bytes):
                        lump = lump.encode()
                    if len(lump):
                        data += lump
                        if (len(data) >= 2) and data[-2:] == b'\r\n':
                            complete_line = 1
                            print(22222)
                            rsp, keep = self.do_command(data)
                            if rsp == None:
                                continue
                            if not isinstance(rsp, bytes):
                                rsp = rsp.encode()
                            self.socket.send(rsp + "\r\n".encode())
                            if keep == 0:
                                print('closed')
                                self.socket.close()
                                return
                    else:
                        return
            except Exception as e:
                print(e)
        return


    def do_command(self, data):
        """执行pop命令"""

        cmd = data[0:4]
        if not cmd:
            return
        cmd = data.split(None, 1)[0]
        cmd = cmd.upper().decode()
        data = data.decode() if isinstance(data, bytes) else data
        keep = 1
        rv = None

        command = Dispatch.dispatch(cmd)
        ret = command(data)
        if cmd == Dispatch.handle_quit:
            keep = 0
        if ret:
            return (ret, keep)
        else:
            return ("250 OK", keep)



class POPServer:
    """
    pop服务，在指定端口监听pop连接，每个连接都会实例化一个engine

    """

    def __init__(self, port, log=None):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind(("", port))
        self._socket.listen(5)
        self._log = log

    def serve(self):
        """
        服务入口
        """
        while 1:
            sock, _ = self._socket.accept()
            engine = POPServerEngine(sock, self._log)
            t = threading.Thread(target=self.handle_connection, args=(engine,))
            t.start()

    def handle_connection(self, engine):
        """处理pop连接"""
        engine.run()
