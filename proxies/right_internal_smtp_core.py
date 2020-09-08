#! --*-- coding: utf-8 --*--

import socket, threading

class SMTPServerInterface:
    """
    smtp标准接口
    """

    def helo(self, args):
        return None

    def mail_from(self, args):
        return None

    def rcpt_to(self, args):
        return None

    def data(self, args):
        return None

    def quit(self, args):
        return None

    def reset(self, args):
        return None


def stripAddress(address):
    """
    去掉smtp数据包中的<>符号
    """
    try:
        start = address.index('<') + 1
        end = address.index('>')
    except:
        return address
    return address[start:end]


def splitTo(address):
    """
    返回用户名和主机名
    """
    try:
        start = address.index('<') + 1
        sep = address.index('@') + 1
        end = address.index('>')
    except:
        return address
    return (address[sep:end], address[start:end],)

class SMTPServerInterfaceDebug(SMTPServerInterface):
    """
    测试用
    """

    def helo(self, args):
        print('Received "helo"', args)

    def mail_from(self, args):
        print('Received "MAIL FROM:"', args)

    def rcpt_to(self, args):
        print('Received "RCPT TO"', args)

    def data(self, args):
        print('Received "DATA"', args)

    def quit(self, args):
        print('Received "QUIT"', args)

    def reset(self, args):
        print('Received "RSET"', args)


class SMTPServerEngine:
    """
    代理核心 实现smtp方法协议
    """

    ST_INIT = 0
    ST_HELO = 1
    ST_MAIL = 2
    ST_RCPT = 3
    ST_DATA = 4
    ST_QUIT = 5
    ST_AUTH = 10
    ST_PASS = 11

    def __init__(self, socket, impl, log):
        self.impl = impl
        self.socket = socket
        self.state = SMTPServerEngine.ST_INIT
        self.log = log

    def run(self):
        """
        运行引擎一直到退出命令
        """
        self.socket.send(bytes("220 Python smtps\r\n".encode()))
        while 1:
            data = b''
            complete_line = 0
            try:
                while not complete_line:
                    lump = self.socket.recv(1024)
                    if not isinstance(lump, bytes):
                        lump = lump.encode()
                    if len(lump):
                        data += lump
                        if (len(data) >= 2) and data[-2:] == b'\r\n':
                            complete_line = 1
                            if self.state != SMTPServerEngine.ST_DATA:
                                rsp, keep = self.do_command(data)
                            else:
                                rsp = self.do_data(data)
                                if rsp == None:
                                    continue
                            if not isinstance(rsp, bytes):
                                rsp = rsp.encode() if not isinstance(rsp, bool) else bytes(rsp)
                            self.socket.send(rsp + "\r\n".encode())

                            if keep == 0:
                                self.socket.close()
                                return
                    else:
                        return
            except:
                import traceback
                traceback.print_exc()
                continue
        return

    def do_command(self, data):
        """执行smtp命令"""
        cmd = data[0:4]
        cmd = cmd.upper().decode()
        data = data.decode() if isinstance(data, bytes) else data
        keep = 1
        rv = None
        print('----->', cmd)
        if cmd == "HELO" or cmd == "EHLO":
            self.state = SMTPServerEngine.ST_HELO
            rv = self.impl.helo(data)
        elif cmd == "RSET":
            rv = self.impl.reset(data)
            self.data_accum = ""
            self.state = SMTPServerEngine.ST_HELO
        elif cmd == "NOOP":
            pass
        elif cmd == "QUIT":
            rv = self.impl.quit(data)
            keep = 0
        elif cmd == "MAIL":
            if self.state != SMTPServerEngine.ST_HELO:
                return ("503 Bad command sequence", 1)
            self.state = SMTPServerEngine.ST_MAIL
            rv = self.impl.mail_from(data)
        elif cmd == "RCPT":
            if (self.state != SMTPServerEngine.ST_MAIL) and (self.state != SMTPServerEngine.ST_RCPT):
                return ("503 Bad command sequence", 1)
            self.state = SMTPServerEngine.ST_RCPT
            rv = self.impl.rcpt_to(data)
        elif cmd == "DATA":
            if self.state != SMTPServerEngine.ST_RCPT:
                return ("503 Bad command sequence", 1)
            self.state = SMTPServerEngine.ST_DATA
            self.data_accum = ""
            return ("354 OK, Enter data, terminated with a \\r\\n.\\r\\n", 1)

        elif cmd == "AUTH" and data[5:10].upper() == "PLAIN":
            self.impl.mail.create_clients()
            self.state = SMTPServerEngine.ST_HELO
            return ("235 Authentication Succeeded", 1)

        elif cmd == "AUTH" and data[5:10].upper() == "LOGIN":
            if self.state != SMTPServerEngine.ST_HELO:
                return ("503 Bad command sequence." + str(self.state), 1)
            self.state = SMTPServerEngine.ST_AUTH

            return ("334 VXNlcm5hbWU6", 1)
        else:
            if self.state == SMTPServerEngine.ST_AUTH:
                self.state = SMTPServerEngine.ST_PASS
                self.log.logdebug('username')
                return ("334 UGFzc3dvcmQ6", 1)
            elif self.state == SMTPServerEngine.ST_PASS:
                self.state = SMTPServerEngine.ST_HELO
                self.impl.mail.create_clients()
                return ("235 Authentication Succeeded", 1)
            else:
                return ("500 unrecogonize, enter again.", 1)

        if rv:
            return (rv, keep)
        else:
            return ("250 OK", keep)

    def do_data(self, data):
        """
        处理数据
        """
        data = data.decode() if isinstance(data, bytes) else data
        self.data_accum = self.data_accum + data
        if len(self.data_accum) > 4 and self.data_accum[-5:] == '\r\n.\r\n':
            self.data_accum = self.data_accum[:-5]
            flag = self.impl.data(self.data_accum)
            self.state = SMTPServerEngine.ST_HELO
            if flag:
                return "250 OK - Data and terminator. found"
            else:
                return flag
        else:
            return None


class SMTPServer:
    """
    smtp服务，在指定端口监听smtp连接，每个连接都会实例化一个engine

    """

    def __init__(self, port, log=None):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind(("", port))
        self._socket.listen(5)
        self._log = log

    def serve(self, impl_class=SMTPServerInterfaceDebug):
        """
        服务入口
        """
        while 1:
            sock, _ = self._socket.accept()
            engine = SMTPServerEngine(sock, impl_class(), self._log)
            t = threading.Thread(target=self.handle_connection, args=(engine,))
            t.start()

    def handle_connection(self, engine):
        """处理smtp连接"""
        engine.run()