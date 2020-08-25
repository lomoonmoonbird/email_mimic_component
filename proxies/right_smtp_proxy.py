# --*-- coding:utf-8 --*--

import email
from base64 import b64encode
from proxies.config import readConfig
from proxies import smtp_core
from concurrent.futures import ThreadPoolExecutor, as_completed
import smtplib
from judge import right_judge
from collections import defaultdict

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
        self.lock = None
        self.share_data = defaultdict(lambda: defaultdict(list))

    def reset_share_data(self, tag):
        del self.share_data[tag]

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
        import smtplib
        from email.parser import HeaderParser
        self.mail.msg = (data)
        parser = HeaderParser()
        headers = parser.parsestr(self.mail.msg)
        print(headers.keys())
        with self.lock:
            tag = headers.get('Tag', "")
            if tag:
                self.share_data[tag]['tags'].append(tag)
                self.share_data[tag]['mails'].append(self.mail.msg)
                right_judge(tag, self.share_data)
                print('【mails】',self.share_data[tag])
                if self.share_data[tag]['choice']:
                    try:
                        host = "localhost"
                        server = smtplib.SMTP(host, port=25)
                        server.ehlo()
                        # mail = email.message_from_string(self.share_data[tag]['choice'])
                        res = server.sendmail(self.mail.frm, self.mail.to, self.share_data[tag]['choice'])
                        print('send mail ', res)
                        self.reset_share_data(tag)
                        server.quit()
                        print("Email Send")
                    except:
                        import traceback
                        traceback.print_exc()

    def send(self, client, sender, receiver, mail):
        print(sender, receiver)
        print(mail)
        senderrs = client.sendmail(sender, receiver, mail)
        client.quit()
        return senderrs



