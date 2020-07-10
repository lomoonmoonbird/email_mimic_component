#! --*-- coding: utf-8 --*--

import imaplib, poplib
import socket, os, logging

logging.basicConfig(format="%(name)s %(levelname)s - %(message)s")
log = logging.getLogger("pop_imap_proxy")
log.setLevel(logging.INFO)

class Connection(object):
    END = "\r\n"
    def __init__(self, conn):
        self.conn = conn
    def __getattr__(self, name):
        return getattr(self.conn, name)
    def sendall(self, data, END=END):
        if len(data) < 50:
            log.debug("send: %r", data)
        else:
            log.debug("send: %r...", data[:50])
        data += END
        self.conn.sendall(data)

    def recvall(self, END=END):
        data = []
        while True:
            chunk = self.conn.recv(4096)
            if END in chunk:
                data.append(chunk[:chunk.index(END)])
                break
            data.append(chunk)
            if len(data) > 1:
                pair = data[-2] + data[-1]
                if END in pair:
                    data[-2] = pair[:pair.index(END)]
                    data.pop()
                    break
        log.debug("recv: %r", "".join(data))
        return "".join(data)

class Message(object):
    def __init__(self, filename):
        msg = open(filename, "r")
        try:
            self.data = data = msg.read()
            self.size = len(data)
            self.top, bot = data.split("\r\n\r\n", 1)
            self.bot = bot.split("\r\n")
        finally:
            msg.close()

def handleUser(data, msg):
    return "+OK user accepted"

def handlePass(data, msg):
    return "+OK pass accepted"

def handleStat(data, msg):
    return "+OK 1 %i" % msg.size

def handleList(data, msg):
    return "+OK 1 messages (%i octets)\r\n1 %i\r\n." % (msg.size, msg.size)

def handleTop(data, msg):
    cmd, num, lines = data.split()
    assert num == "1", "unknown message number: %s" % num
    lines = int(lines)
    text = msg.top + "\r\n\r\n" + "\r\n".join(msg.bot[:lines])
    return "+OK top of message follows\r\n%s\r\n." % text

def handleRetr(data, msg):
    log.info("message sent")
    return "+OK %i octets\r\n%s\r\n." % (msg.size, msg.data)

def handleDele(data, msg):
    return "+OK message 1 deleted"

def handleNoop(data, msg):
    return "+OK"

def handleQuit(data, msg):
    return "+OK proxy POP3 server signing off"

dispatch = dict(
    USER=handleUser,
    PASS=handlePass,
    STAT=handleStat,
    LIST=handleList,
    TOP=handleTop,
    RETR=handleRetr,
    DELE=handleDele,
    NOOP=handleNoop,
    QUIT=handleQuit,
)

class proxy_server():
    def serve(host, port, filename):
        assert os.path.exists(filename)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((host, port))
        try:
            if host:
                hostname = host
            else:
                hostname = "localhost"
            log.info("pop POP3 serving '%s' on %s:%s", filename, hostname, port)
            while True:
                sock.listen(1)
                conn, addr = sock.accept()
                log.debug('Connected by %s', addr)
                try:
                    msg = Message(filename)
                    conn = Connection(conn)
                    conn.sendall("+OK proxy file-based pop3 server ready")
                    while True:
                        data = conn.recvall()
                        command = data.split(None, 1)[0]
                        try:
                            cmd = dispatch[command]
                        except KeyError:
                            conn.sendall("-ERR unknown command")
                        else:
                            conn.sendall(cmd(data, msg))
                            if cmd is handleQuit:
                                break
                finally:
                    conn.close()
                    msg = None
        except (SystemExit, KeyboardInterrupt):
            log.info("proxy stopped")
        except Exception as ex:
            log.critical("fatal error", exc_info=ex)
        finally:
            sock.shutdown(socket.SHUT_RDWR)
            sock.close()


class pop_imap_proxy:

    def recv_email_by_pop3(self):
        # 邮件接收的邮箱
        email_address = "jinpeng"
        # 邮件接收的邮箱的密码
        email_password = "jinpeng"
        # 邮箱对应的imap地址
        pop_server_host = "mail.example.com"
        # pop服务器的监听端口
        pop_server_port = 110

        email_server = None
        try:
            email_server = poplib.POP3(host=pop_server_host, port=pop_server_port, timeout=10)
        except:
            exit(1)
        try:
            # 验证邮箱是否存在
            email_server.user(email_address)
        except:
            exit(1)
        try:
            # 验证邮箱密码是否正确
            email_server.pass_(email_password)
        except:
            exit(1)

        email_count = len(email_server.list()[1])
        resp, lines, octets = email_server.retr(email_count)
        email_content = b'\r\n'.join(lines)
        email_content = email_content.decode()
        print(email_content)

        email_server.close()

    def recv_email_by_imap4(self):
        # 邮件接收的邮箱
        email_address = "jinpeng"
        # 邮件接收的邮箱的密码
        email_password = "jinpeng"
        # 邮箱对应的imap地址
        imap_server_host = "mail.example.com"
        # 邮箱对应的imap服务器的监听端口
        imap_server_port = 143

        email_server = None

        try:
            email_server = imaplib.IMAP4(host=imap_server_host, port=imap_server_port)
        except:
            import traceback
            traceback.print_exc()
            exit(1)
        try:
            # 验证邮箱及密码是否正确
            email_server.login(email_address, email_password)
        except:
            exit(1)

        email_server.select()
        email_count = len(email_server.search(None, 'ALL')[1][0].split())
        typ, email_content = email_server.fetch(f'{email_count}'.encode(), '(RFC822)')
        email_content = email_content[0][1].decode()
        email_server.close()
        email_server.logout()

if __name__ == "__main__":
    # 实例化
    email_client = pop_imap_proxy()
    email_client.recv_email_by_pop3()
    # email_client.recv_email_by_imap4()