#! --*-- coding:utf-8 --*--

import socket, threading
import poplib, re
from proxies.config import readConfig
from judge import left_judge
from collections import defaultdict

DEFAULT_KEY = "pop_proxy"
MAX_CLIENT = 10
CRLF = b'\r\n'
CONFIG_PATH = 'proxies/pop_config.ini'
smtpcfg = readConfig(CONFIG_PATH)

Tagged_Request = re.compile(
    r'(?P<command>[A-Z]*)'
    r'(\s(?P<flags>.*))?', flags=re.IGNORECASE)

Tagged_Response= re.compile(r'\A(?P<tag>[A-Z0-9]+)'
    r'\s(OK)'
    r'(\s\[(?P<flags>.*)\])?'
    r'\s(?P<command>[A-Z]*)', flags=re.IGNORECASE)


class Dispatch():


    def __init__(self, client_socket, key):
        self.client_socket = client_socket
        self.server_socket = None
        self.key = key
        self.client_listening = True
        self.request = ""
        self.client_tag = ""
        self.client_command = ""
        self.current_folder = ""
        self.boxes = []
        self.server_sockets = []
        self.response_map = defaultdict(list)

        try:
           self.send_to_client('+OK proxy ready.')
           self.listen_client()
        except (BrokenPipeError, ConnectionResetError):
            print("connection closed")
        except ValueError as e:
            print("[ERROR]", e)

    def listen_client(self):
        """监听客户端的命令"""
        while self.client_listening:
            for request in self.recv_from_client().split('\r\n'):
                match = Tagged_Request.match(request)

                if not match:
                    self.send_to_client(self.error("Incorrect request"))
                    raise ValueError('Error while listening the client: '
                        + request + ' contains no tag and/or no command')

                self.client_command = match.group('command').upper()
                self.client_flags = match.group('flags')
                self.request = request

                cmd = self.dispatch(self.client_command)
                print('cmd--------------》', self.client_command)
                if cmd:
                    try:
                        cmd()
                    except Exception:
                        import traceback
                        traceback.print_exc()
                else:
                    print('no command')
                    self.send_to_client("+OK")


    def listen_server(self, server_tag):
        """ 监听pop邮件服务，通过servertag绑定响应的客户端，处理完整的服务器命令响应，"""

        while True:

            response = self.recv_from_server()
            response_match = Tagged_Response.match(response)

            #完整命令响应
            if response_match:
                server_response_tag = response_match.group('tag') #判断tag
                if server_tag == server_response_tag:
                    self.boxes.append([response])
                    self.send_to_client(response.replace(server_response_tag, self.client_tag, 1))
                    return

            #没有tag
            self.send_to_client(response)

            if response.startswith('+') and self.client_command.upper() != 'FETCH':
                #持续监听
                client_sequence = self.recv_from_client()
                while client_sequence != '' and not client_sequence.endswith(
                        '\r\n'):  # Client sequence ends with empty request
                    self.send_to_server(client_sequence)
                    client_sequence = self.recv_from_client()
                self.send_to_server(client_sequence)

    def listen_server_v2(self, server_tag, server_socket):
        """ 监听pop邮件服务，通过servertag绑定响应的客户端，处理完整的服务器命令响应，"""

        while True:

            response = self.recv_from_server_v2(server_socket)
            response_match = Tagged_Response.match(response)
            #完整命令响应
            if response_match:
                server_response_tag = response_match.group('tag') #判断tag
                if server_tag == server_response_tag:

                    # self.send_to_client(response.replace(server_response_tag, self.client_tag, 1))
                    self.response_map[server_socket.socket().fileno()].append(response)
                    return

            #没有tag
            # self.send_to_client(response)
            self.response_map[server_socket.socket().fileno()].append(response)

            if response.startswith('+') and self.client_command.upper() != 'FETCH':
                #持续监听
                client_sequence = self.recv_from_client()
                while client_sequence != '' and not client_sequence.endswith(
                        '\r\n'):  # Client sequence ends with empty request
                    self.send_to_server_v2(client_sequence, server_socket)
                    client_sequence = self.recv_from_client()
                self.send_to_server_v2(client_sequence, server_socket)

    def connect_server(self, username, password, host):
        """ 连接真正的pop服务器"""

        username = self.remove_quotation_marks(username)
        password = self.remove_quotation_marks(password)
        self.server_socket = poplib.POP3(host)

        try:
            self.server_socket.user(username)
            self.server_socket.pass_(password)

        except Exception as e:
            self.send_to_client(self.failure())
            raise ValueError('Error while connecting to the server: '
                             + 'Invalid credentials: ' + username + " / " + password)
        # self.send_to_client(self.success())

    def connect_server_v2(self, username, password, host):
        """ 连接真正的pop服务器"""

        username = self.remove_quotation_marks(username)
        password = self.remove_quotation_marks(password)

        while 1:
            try:
                server_socket = poplib.POP3(host)
                server_socket.user(username)
                server_socket.pass_(password)
                self.response_map[id(server_socket)].append("+OK Logged in.")
                return server_socket
            except poplib.error_proto as e:
                import traceback
                traceback.print_exc()
                continue
            except Exception as e:
                raise ValueError('Error while connecting to the server: '
                                 + 'Invalid credentials: ' + username + " / " + password)


    def recv_from_client(self):
        """ 返回接收客户端去掉CRLF的请求 """

        b_request = self.client_socket.recv(1024)
        str_request = b_request.decode('utf-8', 'replace')[:-2]  # decode and remove CRLF

        return str_request

    def recv_from_server_v2(self, server_socket):
        """ 返回接收服务端端去掉CRLF的请求 """
        b_response = server_socket._get_line()
        str_response = b_response.decode('utf-8', 'replace')

        return str_response

    def recv_from_server(self):
        """ 返回接收服务端端去掉CRLF的请求 """

        b_response = self.server_socket._get_line()
        str_response = b_response.decode('utf-8', 'replace')

        return str_response

    def transmit(self):
        """ 将客户端的tag替换为服务端的tag，并发送请求到服务端，然后监听服务端 """

        server_tag = self.server_socket._new_tag().decode()
        self.send_to_server(self.request.replace(self.client_tag, server_tag, 1))
        self.listen_server(server_tag)

    def transmit_v2(self, server_socket):
        """ 将客户端的tag替换为服务端的tag，并发送请求到服务端，然后监听服务端 """
        server_tag = server_socket._new_tag().decode()
        self.send_to_server_v2(self.request.replace(self.client_tag, server_tag, 1), server_socket)
        self.listen_server_v2(server_tag, server_socket)

    # def send_to_client(self, str_data):
    #     """ 发送客户端"""
    #     b_data = str_data.encode('utf-8', 'replace') + CRLF
    #     self.client_socket.send(b_data)
    #
    # def send_to_server(self, str_data):
    #     """发送服务端"""
    #     b_data = str_data.encode('utf-8', 'replace') + CRLF
    #     self.server_socket.send(b_data)

    def destroy(self):
        self.response_map = defaultdict(list)

    def send_to_client(self, str_data):
        """ 发送客户端"""
        b_data = str_data.encode('utf-8', 'replace') + CRLF if not isinstance(str_data, bytes) else str_data + CRLF
        self.client_socket.send(b_data)

    def send_to_server(self, str_data):
        """发送服务端"""
        b_data = str_data.encode('utf-8', 'replace') + CRLF if not isinstance(str_data, bytes) else str_data + CRLF
        self.server_socket.sendall(b_data)

    def send_to_server_v2(self, str_data, server_socket):
        """发送服务端"""
        b_data = str_data.encode('utf-8', 'replace') + CRLF
        server_socket.send(b_data)

    def success(self):
        """ 命令成功的响应体 """
        return self.client_tag + ' OK ' + self.client_command + ' completed.'

    def failure(self):
        """ 命令失败的响应体 """
        return self.client_tag + ' NO ' + self.client_command + ' failed.'

    def error(self, msg):
        """ 错误命令响应体 """
        return self.client_tag + ' BAD ' + msg

    def remove_quotation_marks(self, text):
        """ 去掉引号 """
        if text.startswith('"') and text.endswith('"'):
            text = text[1:-1]
        return text

    def set_current_folder(self, folder):
        """ 设置用户邮箱的文件夹名称 """
        self.current_folder = self.remove_quotation_marks(folder)

    def saying(self, res):
        for saying in res:
            self.send_to_client(saying)

    def dispatch(self, cmd):
        return dict(
            USER=self.handle_user,
            PASS=self.handle_pass,
            STAT=self.handle_stat,
            LIST=self.handle_list,
            TOP=self.handle_top,
            RETR=self.handle_retr,
            DELE=self.handle_dele,
            NOOP=self.handle_noop,
            QUIT=self.handle_quit,
            LOGIN=self.handle_login,
            UIDL=self.handle_uidl,
            AUTH = self.handle_auth,
            CAPA = self.handle_capa,
        ).get(cmd, None)

    def handle_capa(self):
        self.saying(["+OK", "PLAIN", "LOGIN", "."])

    def handle_auth(self):
        self.saying(["+OK", "CAPA", "TOP", "UIDL", "RESP-CODES", "PIPELINING", "AUTH-RESP-CODE", "USER", "SASL PLAIN LOGIN", '.'])

    def handle_uidl(self):
        self.destroy()
        for s_socket in self.server_sockets:
            msg, mail_ids, _ = s_socket.uidl()
            mail_ids = b''.join([x + b"\r\n" for x in mail_ids])
            self.response_map[id(s_socket)].append(msg + b'\r\n' + mail_ids + b'.')
        res = left_judge(self.response_map, switch='off')
        print('uidl res', res)
        self.saying(res)

    def handle_login(self):
        username, password = self.client_flags.split(" ")
        hosts = [(hp.split(':')[0], hp.split(':')[1]) for hp in smtpcfg['config'].distribute_hosts.split(",")]
        self.connect_server(username, password, hosts[0][0])
        # self.connect_server(username, password, 'mail2.example.com')

    def handle_user(self):
        self.username = self.client_flags
        self.send_to_client("+OK")

    def handle_pass(self):
        self.password = self.client_flags
        hosts = [(hp.split(':')[0], hp.split(':')[1]) for hp in smtpcfg['config'].distribute_hosts.split(",")]
        # self.connect_server(self.username, self.password, hosts[0][0])
        # self.send_to_client("+OK Logged in.")
        for host in hosts:
            server_sock = self.connect_server_v2(self.username, self.password, host[0])
            self.server_sockets.append(server_sock)
        print(self.server_sockets)
        res = left_judge(self.response_map, switch='off')
        print('pass res' ,res)
        self.saying(res)

    def handle_stat(self):
        self.destroy()
        for s_socket in self.server_sockets:
            num, bytes = s_socket.stat()
            self.response_map[id(s_socket)].append("+OK "+ str(num) + ' ' + str(bytes))
        res = left_judge(self.response_map, switch='off')
        print('stat res', res)
        self.saying(res)


    def handle_list(self):
        self.destroy()
        for s_socket in self.server_sockets:
            msg, mail_ids, _ = s_socket.list()
            mail_ids = b''.join([x + b"\r\n" for x in mail_ids])
            self.response_map[id(s_socket)].append(msg + b'\r\n' + mail_ids +b'.')
        res = left_judge(self.response_map, switch='off')
        print('list res', res)
        self.saying(res)

    def handle_noop(self):
        self.destroy()
        for s_socket in self.server_sockets:
            resp = s_socket.noop()
            self.response_map[id(s_socket)].append(resp)
        res = left_judge(self.response_map, switch='off')
        print('noop res', res)
        self.saying(res)

    def handle_top(self):
        start, end = self.client_flags.split(" ")
        self.destroy()
        print(self.client_flags, start ,end)
        # for s_socket in self.server_sockets:
        #     msg, mails, _ = s_socket.top(start, end)
        #     mails = [x + b"\r\n" for x in mails]
        #     mails.insert(0, msg)
        #     self.response_map[id(s_socket)] = mails
        for s_socket in self.server_sockets:
            msg, mails, _ = s_socket.top(start, end)
            mails = b''.join([x + b"\r\n" for x in mails])
            # mails.insert(0, msg)
            self.response_map[id(s_socket)].append(msg + b'\r\n' + mails + b'.')
        res = left_judge(self.response_map, switch='off')
        print('top res', res)
        self.saying(res)


    def handle_retr(self):
        self.destroy()
        for s_socket in self.server_sockets:
            res, lines, octets  = s_socket.retr(self.client_flags)
            lines =  [x + b"\r\n" for x in lines] + [b'.']
            lines.insert(0, res)
            self.response_map[id(s_socket)] = lines
        res = left_judge(self.response_map, switch='off')
        print('retr res', res)
        self.saying(res)

    def handle_dele(self):
        return "+OK message 1 deleted"

    def handle_quit(self):
        self.destroy()
        for s_socket in self.server_sockets:
            rsp = s_socket.quit()
            self.response_map[id(s_socket)].append(rsp)
        res = left_judge(self.response_map, switch='off')
        self.saying(res)
        self.client_socket.close()

class POPServer:
    """
    pop服务，在指定端口监听imap连接，每个连接都会实例化一个engine

    """

    def __init__(self, port, log=None, key = DEFAULT_KEY, max_client=MAX_CLIENT):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, (8 * b'\x00') + (800000).to_bytes(8, 'little'))
        # self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDTIMEO, (8 * b'\x00') + (100000).to_bytes(8, 'little'))
        self._socket.bind(("", port))
        self._socket.listen(max_client)
        self._log = log
        self.key = key

    def serve(self):
        """
        服务入口
        """

        while 1:
            sock, _ = self._socket.accept()
            t = threading.Thread(target=self.handle_connection, args=(sock,))
            t.start()

    def handle_connection(self, sock):
        """处理pop连接"""
        Dispatch(sock, self.key)
