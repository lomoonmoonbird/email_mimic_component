# --*-- coding:utf-8 --*--

import email
from base64 import b64encode
from proxies.config import readConfig
from proxies import smtp_core
from concurrent.futures import ThreadPoolExecutor, as_completed
import smtplib

CONFIG_PATH = 'proxies/smtp_config.ini'
smtpcfg = readConfig(CONFIG_PATH)


class Mail():
    """
    需要代理的邮件类
    """

    def __init__(self):
        self.msg = None
        self.to = []
        self.frm = ''
        self.mail_clients = []

    def create_clients(self):
        hosts = [(hp.split(':')[0], hp.split(':')[1]) for hp in smtpcfg['config'].distribute_hosts.split(",")]
        for host, port in hosts:
            server = smtplib.SMTP(host, port)
            server.connect(host, port)
            server.set_debuglevel(smtpcfg['config'].debuglevel)
            server.ehlo()
            self.mail_clients.append(server)

def encode_plain(user, password):
    """ 加密user password"""
    return b64encode("\0%s\0%s" % (user, password))


class SMTPProxy(smtp_core.SMTPServerInterface):
    """
    接收中转的邮件 每次SMTP连接建立的时候都会实例化，每次处理一个邮件
    """
    HELO = (
        "250-PIPELINING",
        "250-SIZE 102400",
        "250-VRFY",
        "250-ETRN",
        "250-STARTTLS",
        "250-AUTH PLAIN LOGIN",
        "250-ENHANCEDSTA",
        "250-8BITMIME",
        "250-DSN",
        "250 SMTPUTF8"
    )

    def __init__(self):
        self.mail = Mail()

    def helo(self, args):
        return '' .join([item + '\r\n' for item in self.HELO])[:-4]

    def mail_from(self, mail):
        """
        邮件发送人部分
        :return:
        """
        self.mail.frm = smtp_core.stripAddress(mail.split(":")[1].strip())

    def rcpt_to(self, mail):
        """
        邮件收件人
        :param mail:
        :return:
        """
        self.mail.to.append(smtp_core.stripAddress(mail.split(":")[1].strip()))

    def change_from(self, new_from):
        """
        修改邮件发送人
        :param new_from:
        :return:
        """
        self.mail.frm = new_from

    def change_to(self, new_to):
        """
        修改邮件接收者
        :param new_to:
        :return:
        """
        msg = email.message_from_string(self.mail.msg)
        msg.replace_header('TO:', new_to)
        self.mail.to = [ new_to ]
        self.mail.msg = str(msg)

    def data(self, data):
        """
        除发件人/收件人外其他数据
        :param data:
        :return:
        """
        import email.utils
        import hashlib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        from email.header import Header

        self.mail.msg = (data)
        md = hashlib.md5()
        md.update(self.mail.msg.encode('utf-8'))
        origin = email.message_from_string(self.mail.msg)
        self.mail.msg = 'Receive: ( SMTP PROXY ) ' + email.utils.formatdate() + '\n' + self.mail.msg
        self.mail.msg = 'Accept-Language: ISO-8859-1,utf-8' + '\n' + self.mail.msg
        self.mail.msg = 'Accept-Language: ISO-8859-1,utf-8' + '\n' + self.mail.msg
        self.mail.msg = 'Tag: ' +  md.hexdigest() + '\n' +self.mail.msg


        # msg = MIMEMultipart()
        # msg['Subject'] = origin.get('Subject', '')
        # msg['From'] = self.mail.frm
        # msg['To'] = self.mail.to[0]
        # msg['reply-to'] = ""
        # msg['X-Priority'] = ""
        # msg['CC'] = ""
        # msg['BCC'] = ""
        # msg['Tag'] = md.hexdigest()
        # msg['Return-Receipt-To'] = self.mail.frm
        # msg["Accept-Language"] = "zh-CN"
        # msg.preamble = 'Event Notification'
        # msg["Accept-Charset"] = "ISO-8859-1,utf-8"
        # msg.attach(MIMEText(data))

        # msg = MIMEText(data, 'plain', 'utf-8')
        # msg['From'] = self.mail.frm
        # msg['To'] = self.mail.to[0]
        # msg['Tag'] = md.hexdigest()
        # msg["Accept-Language"] = "zh-CN"
        # msg["Accept-Charset"] = "ISO-8859-1,utf-8"

        obj_list = []

        try_time = 0
        while try_time < 3:
            with ThreadPoolExecutor(max_workers=3) as e:
                try:
                    for client in self.mail.mail_clients:
                        obj = e.submit(self.send, client, self.mail.frm, self.mail.to[0], self.mail.msg)
                        obj_list.append(obj)
                    for future in as_completed(obj_list):
                        senderrs = future.result()
                        if senderrs:
                            return False
                    return True
                except smtplib.SMTPServerDisconnected as e:
                    try_time += 1
                    print('error a ')
                    continue
                except:
                    import traceback
                    traceback.print_exc()
                    print('error b')
                    print(client.__dict__)
                    return False

    def send(self, client, sender, receiver, mail):
        senderrs = client.sendmail(sender, receiver, mail)
        print(senderrs)
        client.quit()
        return senderrs



