#! --*-- coding:utf-8 --*--

import socket, threading
import imaplib, re
from proxies.config import readConfig
from collections import defaultdict
from judge import left_judge

DEFAULT_KEY = "imap_proxy"
MAX_CLIENT = 10
CRLF = b'\r\n'
CONFIG_PATH = 'proxies/imap_config.ini'
smtpcfg = readConfig(CONFIG_PATH)

Tagged_Request = re.compile(r'(?P<tag>[A-Z0-9]+)'
    r'(\s(UID))?'
    r'\s(?P<command>[A-Z]*)'
    r'(\s(?P<flags>.*))?', flags=re.IGNORECASE)

Tagged_Response= re.compile(r'\A(?P<tag>[A-Z0-9]+)'
    r'\s(OK)'
    r'(\s\[(?P<flags>.*)\])?'
    r'\s(?P<command>[A-Z]*)', flags=re.IGNORECASE)


class Dispatch():

    CAPABILITIES = (
        "IMAP4rev1",
        "SASL_IR",
        "LOGIN-REFERRALS",
        "ID",
        "ENABLE",
        "IDLE",
        "LITERAL+"
        "AUTH=PLAIN",
        "AUTH=LOGIN"
    )

    def __init__(self, socket, key):
        self.client_socket = socket
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


    def run(self):
        try:
            self.send_to_client('* OK proxy ready.')
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
                    continue
                    # raise ValueError('Error while listening the client: '
                    #     + request + ' contains no tag and/or no command')

                self.client_tag = match.group('tag')
                self.client_command = match.group('command').upper()
                self.client_flags = match.group('flags')
                self.request = request
                print("[from client]:", self.client_tag,self.client_command,self.client_flags  )
                cmd = self.dispatch(self.client_command)
                if cmd:
                    try:
                        cmd()
                    except Exception:
                        import traceback
                        traceback.print_exc()
                        break
                else:
                    for s_socket in self.server_sockets:
                        self.transmit_v2(s_socket)
                    res = left_judge(self.response_map)
                    self.saying(res)

    def listen_server_v2(self, server_tag, server_socket):
        """ 监听imap邮件服务，通过servertag绑定响应的客户端，处理完整的服务器命令响应，"""

        while True:

            response = self.recv_from_server_v2(server_socket)

            response_match = Tagged_Response.match(response)
            #完整命令响应
            if response_match:
                server_response_tag = response_match.group('tag') #判断tag
                if server_tag == server_response_tag:
                    self.response_map[server_socket.socket().fileno()].append(response.replace(server_response_tag, self.client_tag, 1))
                    return

            # if self.client_command.upper() == 'IDLE':
            #     self.response_map[server_socket.socket().fileno()].append(response)
            #     return

            #没有tag
            self.response_map[server_socket.socket().fileno()].append(response)

            if response.startswith('+') and self.client_command.upper() != 'FETCH':
                #持续监听
                client_sequence = self.recv_from_client()
                while client_sequence != '' and not client_sequence.endswith(
                        '\r\n'):
                    self.send_to_server_v2(client_sequence, server_socket)
                    client_sequence = self.recv_from_client()
                self.send_to_server_v2(client_sequence, server_socket)


    def connect_server_v2(self, username, password, host):
        """ 连接真正的imap服务器"""

        username = self.remove_quotation_marks(username)
        password = self.remove_quotation_marks(password)

        # print("Trying to connect ", username, password, host)
        while 1:
            try:
                server_socket = imaplib.IMAP4(host)
                r, d = server_socket.login(username, password)
                if r == 'OK':
                    self.response_map[server_socket.socket().fileno()].append(self.success())
                    return server_socket
                server_socket.logout()
            except imaplib.IMAP4.abort:
                import traceback
                traceback.print_exc()
                continue
            except imaplib.IMAP4.error:
                import traceback
                traceback.print_exc()
                raise ValueError('Error while connecting to the server: '
                                 + 'Invalid credentials: ' + username + " / " + password + " / "+ host)



    def recv_from_client(self):
        """ 返回接收客户端去掉CRLF的请求 """
        b_request = self.client_socket.recv(1024)
        str_request = b_request.decode('utf-8', 'replace')[:-2]  # decode and remove CRLF
        return str_request

    def recv_from_server(self):
        """ 返回接收服务端端去掉CRLF的请求 """
        b_response = self.server_socket._get_line()
        str_response = b_response.decode('utf-8', 'replace')
        return str_response

    def recv_from_server_v2(self, server_socket):
        """ 返回接收服务端端去掉CRLF的请求 """
        b_response = server_socket._get_line()
        str_response = b_response.decode('utf-8', 'replace')
        return str_response

    def transmit_v2(self, server_socket):
        """ 将客户端的tag替换为服务端的tag，并发送请求到服务端，然后监听服务端 """
        server_tag = server_socket._new_tag().decode()
        # print('@@@@@@@@@@@@@@@', id(server_socket), self.request.replace(self.client_tag, server_tag, 1))
        self.send_to_server_v2(self.request.replace(self.client_tag, server_tag, 1), server_socket)
        self.listen_server_v2(server_tag, server_socket)

    def send_to_client(self, str_data):
        """ 发送客户端"""
        b_data = str_data.encode('utf-8', 'replace') + CRLF
        self.client_socket.send(b_data)

    def send_to_server_v2(self, str_data, server_socket):
        """发送服务端"""
        b_data = str_data.encode('utf-8', 'replace') + CRLF
        server_socket.send(b_data)

    def send_to_server(self, str_data):
        """发送服务端"""
        b_data = str_data.encode('utf-8', 'replace') + CRLF
        self.server_socket.send(b_data)

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

    def destroy(self):
        self.response_map = defaultdict(list)

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
            LSUB = self.handle_lsub,
            STATUS = self.handler_status,
            DELE=self.handle_dele,
            NOOP=self.handle_noop,
            SELECT=self.handle_select,
            QUIT=self.handle_quit,
            LOGIN=self.handle_login,
            CAPABILITY=self.handle_capa,
            IDLE = self.handle_idle,
            ID = self.handle_id,
            AUTHENTICATE = self.handle_authenticate,
            FETCH = self.handle_fetch
        ).get(cmd, None)

    def handle_authenticate(self):
        self.saying(["C2 OK    ."])

    def handle_idle(self):
        self.destroy()
        for s_socket in self.server_sockets:
            self.transmit_v2(s_socket)
        res = left_judge(self.response_map, switch='off')
        print('idle res', res)
        self.saying(res)

    def handler_status(self):
        self.destroy()
        for s_socket in self.server_sockets:
            self.transmit_v2(s_socket)
        res = left_judge(self.response_map, switch='off')
        print('status res', res)
        self.saying(res)

    def handle_lsub(self):
        self.destroy()
        for s_socket in self.server_sockets:
            self.transmit_v2(s_socket)
        res = left_judge(self.response_map, switch='off')
        print('lsub res', res)
        self.saying(res)

    def handle_select(self):
        self.destroy()
        for s_socket in self.server_sockets:
            self.transmit_v2(s_socket)
        res = left_judge(self.response_map, switch='off')
        print('select res', res)
        self.saying(res)

    def handle_fetch(self):
        self.destroy()
        for s_socket in self.server_sockets:
            self.transmit_v2(s_socket)
        res = left_judge(self.response_map, switch='off')
        print('fetch res', res)
        self.saying(res)

    def handle_id(self):
        self.destroy()
        # if not self.server_socket:
        #         #     self.send_to_client('NO user not valid')
        #         # for s_socket in self.server_sockets:
        #         #     self.transmit_v2(s_socket)
        #         # res = left_judge(self.response_map, switch='off')
        #         # print('id res', self.response_map)
        res = ['* ID ("name" "Dovecot")', 'C2 OK ID completed (0.001 + 0.000 secs).']
        self.saying(res)

    def handle_capa(self):
        self.destroy()
        self.send_to_client('* CAPABILITY ' + ' '.join(cap for cap in self.CAPABILITIES) + ' +')
        self.send_to_client(self.success())

    def handle_login(self):
        print(len(self.server_sockets), '@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
        self.destroy()
        self.server_sockets = []
        username, password = self.client_flags.split(" ")
        hosts = [(hp.split(':')[0], hp.split(':')[1]) for hp in smtpcfg['config'].distribute_hosts.split(",")]
        for host in hosts:
            server_sock = self.connect_server_v2(username, password, host[0])
            self.server_sockets.append(server_sock)
        res = left_judge(self.response_map, switch='off')
        print('login res', res)
        self.saying(res)


    def handle_user(self):
        pass

    def handle_pass(self):
        pass

    def handle_stat(self):
        print('stat')
        pass

    def handle_list(self):
        self.destroy()
        for s_socket in self.server_sockets:
            self.transmit_v2(s_socket)
        res = left_judge(self.response_map, switch='off')
        # res = [x + '\r\n' for x in res]
        print('list res',type(res[0]),res)
        self.saying(res)

    def handle_top(self):
        print('top')
        return None

    def handle_retr(self):
        print('retr')
        pass

    def handle_dele(self):
        return "+OK message 1 deleted"

    def handle_noop(self):
        self.destroy()
        for s_socket in self.server_sockets:
            self.transmit_v2(s_socket)
        res = left_judge(self.response_map, switch='off')
        print('noop res', res)
        self.saying(res)

    def handle_quit(self):
        self.client_listening = False

class IMAPServer:
    """
    imap服务，在指定端口监听imap连接，每个连接都会实例化一个engine

    """

    def __init__(self, port, log=None, key = DEFAULT_KEY, max_client=MAX_CLIENT):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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
        """处理imap连接"""
        print('!!!!!!!!!!')
        Dispatch(sock, self.key).run()
