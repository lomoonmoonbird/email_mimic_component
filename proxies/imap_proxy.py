"""
    Implementation of the proxy
"""

import sys, socket, ssl, re, base64, threading, argparse, imaplib



DEFAULT_KEY = 'secret-proxy'

MAX_CLIENT = 5

IMAP_PORT, IMAP_SSL_PORT = 143, 993
CRLF = b'\r\n'

Tagged_Request = re.compile(r'(?P<tag>[A-Z0-9]+)'
                            r'(\s(UID))?'
                            r'\s(?P<command>[A-Z]*)'
                            r'(\s(?P<flags>.*))?', flags=re.IGNORECASE)
Tagged_Response = re.compile(r'\A(?P<tag>[A-Z0-9]+)'
                             r'\s(OK)'
                             r'(\s\[(?P<flags>.*)\])?'
                             r'\s(?P<command>[A-Z]*)', flags=re.IGNORECASE)

CAPABILITIES = (
    'IMAP4',
    'IMAP4rev1',
    'AUTH=PLAIN',
    'UIDPLUS',
    'MOVE',
    'ID',
    'UNSELECT',
    'CHILDREN',
    'NAMESPACE'
)

HOSTS = {
    'mmb': 'mail.moonmoonbird.com'  # for Travis-CI
}

COMMANDS = (
    'authenticate',
    'capability',
    'login',
    'logout',
    'select',
    'move',
    'fetch'
)


class IMAP_Proxy:

    def __init__(self, port=None, host='', certfile=None, key=DEFAULT_KEY, max_client=MAX_CLIENT, verbose=False,
                 ipv6=False):
        self.verbose = verbose
        self.certfile = certfile
        self.key = key

        if not port:  # Set default port
            port = IMAP_SSL_PORT if certfile else IMAP_PORT

        if not max_client:
            max_client = MAX_CLIENT

        # IPv4 or IPv6
        addr_fam = socket.AF_INET6 if ipv6 else socket.AF_INET
        self.sock = socket.socket(addr_fam, socket.SOCK_STREAM)

        self.sock.bind(('', port))
        self.sock.listen(max_client)
        self.listen()

    def listen(self):
        while True:
            try:
                ssock, addr = self.sock.accept()
                if self.certfile:  # Add SSL/TLS
                    ssock = ssl.wrap_socket(ssock, certfile=self.certfile, server_side=True)

                # Connect the proxy with the client
                threading.Thread(target=self.new_connection, args=(ssock,)).start()
            except KeyboardInterrupt:
                break
            except ssl.SSLError as e:
                raise

        if self.sock:
            self.sock.close()

    def new_connection(self, ssock):
        Connection(ssock, self.key, self.verbose)


class Connection:

    def __init__(self, socket, key, verbose=False):
        self.verbose = verbose
        self.key = key
        self.conn_client = socket
        self.conn_server = None

        try:
            self.send_to_client('* OK Service Ready.')  # Server greeting
            self.listen_client()
        except ssl.SSLError:
            pass
        except (BrokenPipeError, ConnectionResetError):
            print('Connections closed')
        except ValueError as e:
            print('[ERROR]', e)

        if self.conn_client:
            self.conn_client.close()

    #       Listen client/server and connect server

    def listen_client(self):
        while self.listen_client:
            for request in self.recv_from_client().split('\r\n'):  # In case of multiple requests

                match = Tagged_Request.match(request)
                if not match:
                    # Not a correct request
                    self.send_to_client(self.error('Incorrect request'))
                    raise ValueError('Error while listening the client: '
                                     + request + ' contains no tag and/or no command')

                self.client_tag = match.group('tag')
                self.client_command = match.group('command').lower()
                self.client_flags = match.group('flags')
                self.request = request

                if self.client_command in COMMANDS:
                    # Command supported by the proxy
                    getattr(self, self.client_command)()
                else:
                    # Command unsupported -> directly transmit to the server
                    self.transmit()

    def transmit(self):
        server_tag = self.conn_server._new_tag().decode()
        self.send_to_server(self.request.replace(self.client_tag, server_tag, 1))
        self.listen_server(server_tag)

    def listen_server(self, server_tag):
        while True:

            response = self.recv_from_server()
            response_match = Tagged_Response.match(response)

            ##   Command completion response
            if response_match:
                server_response_tag = response_match.group('tag')
                if server_tag == server_response_tag:
                    # Verify the command completion corresponds to the client command
                    self.send_to_client(response.replace(server_response_tag, self.client_tag, 1))
                    return

                    ##   Untagged or continuation response or data messages
            self.send_to_client(response)

            if response.startswith('+') and self.client_command.upper() != 'FETCH':
                ##   Continuation response
                client_sequence = self.recv_from_client()
                while client_sequence != '' and not client_sequence.endswith(
                        '\r\n'):  # Client sequence ends with empty request
                    self.send_to_server(client_sequence)
                    client_sequence = self.recv_from_client()
                self.send_to_server(client_sequence)

    def connect_server(self, username, password):
        username = self.remove_quotation_marks(username)
        password = self.remove_quotation_marks(password)

        domains = username  # Remove before '@' and remove '.com' / '.be' / ...
        domain = 'mmb'

        try:
            hostname = HOSTS[domain]
        except KeyError:
            self.send_to_client(self.error('Unknown hostname'))
            raise ValueError('Error while connecting to the server: '
                             + 'Invalid domain name ' + domain)

        print("Trying to connect ", username)
        self.conn_server = imaplib.IMAP4(hostname)

        try:
            self.conn_server.login(username, password)
        except imaplib.IMAP4.error:
            self.send_to_client(self.failure())
            raise ValueError('Error while connecting to the server: '
                             + 'Invalid credentials: ' + username + " / " + password)

        self.send_to_client(self.success())

    #       Mandatory supported IMAP commands

    def capability(self):
        self.send_to_client('* CAPABILITY ' + ' '.join(cap for cap in CAPABILITIES) + ' +')
        self.send_to_client(self.success())

    def authenticate(self):
        auth_type = self.client_flags.split(' ')[0].lower()
        getattr(self, self.client_command + "_" + auth_type)()

    def authenticate_plain(self):
        self.send_to_client('+')
        request = self.recv_from_client()
        (empty, busername, bpassword) = base64.b64decode(request).split(b'\x00')
        username = busername.decode()
        password = bpassword.decode()
        self.connect_server(username, password)

    def login(self):
        (username, password) = self.client_flags.split(' ')
        self.connect_server(username, password)

    def logout(self):
        self.listen_client = False
        self.transmit()

    def select(self):
        self.set_current_folder(self.client_flags)
        self.transmit()


    def fetch(self):
        self.transmit()

    def move(self):
        self.transmit()


    def success(self):
        return self.client_tag + ' OK ' + self.client_command + ' completed.'

    def failure(self):
        return self.client_tag + ' NO ' + self.client_command + ' failed.'

    def error(self, msg):
        return self.client_tag + ' BAD ' + msg


    def send_to_client(self, str_data):

        b_data = str_data.encode('utf-8', 'replace') + CRLF
        self.conn_client.send(b_data)

        if self.verbose:
            print("[<--]: ", b_data)

    def recv_from_client(self):
        b_request = self.conn_client.recv(1024)
        str_request = b_request.decode('utf-8', 'replace')[:-2]  # decode and remove CRLF

        if self.verbose:
            print("[-->]: ", b_request)

        return str_request

    def send_to_server(self, str_data):
        b_data = str_data.encode('utf-8', 'replace') + CRLF
        self.conn_server.send(b_data)

        if self.verbose:
            print("  [-->]: ", b_data)

    def recv_from_server(self):
        b_response = self.conn_server._get_line()
        str_response = b_response.decode('utf-8', 'replace')

        if self.verbose:
            print("  [<--]: ", b_response)

        return str_response


    def set_current_folder(self, folder):
        self.current_folder = self.remove_quotation_marks(folder)

    def remove_quotation_marks(self, text):
        if text.startswith('"') and text.endswith('"'):
            text = text[1:-1]
        return text