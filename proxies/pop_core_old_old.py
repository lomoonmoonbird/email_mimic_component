import socket, string, threading
import poplib


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
            QUIT=cls.handle_quit,
        ).get(cmd)

    @classmethod
    def recv_email_by_pop3(cls, address, password, host, port):

        email_server = None
        try:
            email_server = poplib.POP3(host=host, port=port, timeout=10)
        except:
            import traceback
            traceback.print_exc()
            exit(1)
        try:
            # 验证邮箱是否存在
            email_server.user(address)
        except:
            import traceback
            traceback.print_exc()
            exit(1)
        try:
            # 验证邮箱密码是否正确
            email_server.pass_(password)
        except:
            import traceback
            traceback.print_exc()
            exit(1)

        email_count = len(email_server.list()[1])
        resp, lines, octets = email_server.retr(email_count)
        email_content = b'\r\n'.join(lines)
        email_content = email_content.decode()
        print(email_content)
        email_server.close()

    @classmethod
    def handle_user(cls):
        return "+OK user accepted"

    @classmethod
    def handle_pass(cls):
        return "+OK pass accepted"

    @classmethod
    def handle_stat(cls):
        return None

    @classmethod
    def handle_list(cls):
        return None

    @classmethod
    def handle_top(cls):
        return None

    @classmethod
    def handle_retr(cls, data, extra={}):
        email_address = extra.get("address", "")
        # 邮件接收的邮箱的密码
        email_password = extra.get("password", "")
        # 邮箱对应的imap地址
        pop_server_host = extra.get("host")
        # pop服务器的监听端口
        pop_server_port = extra.get("port", 110)
        print(extra)
        email_server = None
        try:
            email_server = poplib.POP3(host=pop_server_host, port=pop_server_port, timeout=10)
        except:
            import traceback
            traceback.print_exc()
            exit(1)
        try:
            # 验证邮箱是否存在
            email_server.user(email_address)
        except:
            import traceback
            traceback.print_exc()
            exit(1)
        try:
            # 验证邮箱密码是否正确
            email_server.pass_(email_password)
        except:
            import traceback
            traceback.print_exc()
            exit(1)

        email_count = len(email_server.list()[1])
        resp, lines, octets = email_server.retr(email_count)
        email_content = b'\r\n'.join(lines)
        # email_content = email_content.decode()
        email_server.close()
        return resp + b"\r\n" + email_content +b"\r\n"

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
                        extra = {"host": "mail.example.com", "port": 110, "address": "jinpeng", "password": "jinpeng"}
                        rsp, keep = self.do_command(data, extra=extra)
                        if rsp == None:
                            continue
                        if not isinstance(rsp, bytes):
                            rsp = rsp.encode()
                        self.socket.send(rsp + "\r\n".encode())

                        if keep == 0:
                            self.socket.close()
                            return
                else:
                    return
        return

    def do_command(self, data, extra={}):
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
        ret = command(data, extra=extra)
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
            t.join()

    def handle_connection(self, engine):
        """处理pop连接"""
        engine.run()