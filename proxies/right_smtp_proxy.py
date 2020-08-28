# --*-- coding:utf-8 --*--

import email
from base64 import b64encode
from proxies.config import readConfig
from proxies import smtp_core
from concurrent.futures import ThreadPoolExecutor, as_completed
import smtplib
from judge import right_judge
from collections import defaultdict
import redis


CONFIG_PATH = 'proxies/right_smtp_config.ini'
smtpcfg = readConfig(CONFIG_PATH)
client = redis.Redis(host=smtpcfg['config'].redis_server,
                     port=smtpcfg['config'].redis_port,
                     db=smtpcfg['config'].redis_db)

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
        # "250-STARTTLS",
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
        import smtplib
        import base64
        from email.parser import HeaderParser
        from email.header import decode_header
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        self.mail.msg = (data)
        parser = HeaderParser()
        headers = parser.parsestr(self.mail.msg)
        tag = headers.get('Tag', "")
        host = headers.get('Host', "")
        print('iam data')
        try:

            if tag and host:
                origin = email.message_from_string(self.mail.msg)
                msg = MIMEMultipart()
                msg['Subject'] = origin['Subject']
                msg['Receive'] = origin['Receive']
                msg['From'] = self.mail.frm
                msg['To'] = self.mail.to[0]
                msg['reply-to'] = ""
                msg['X-Priority'] = ""
                msg['CC'] = ""
                msg['BCC'] = ""
                msg['Tag'] = origin['Tag']
                msg['MD5'] = origin['MD5']
                msg['Return-Receipt-To'] = self.mail.frm
                msg["Accept-Language"] = "zh-CN"
                msg.preamble = 'Event Notification'
                msg["Accept-Charset"] = "ISO-8859-1,utf-8"

                print(self.mail.msg)
                if origin.is_multipart():
                    print('multipart')
                    for part in origin.walk():
                            ctype = part.get_content_type()
                            cdispo = str(part.get('Content-Disposition'))

                            if ctype == 'text/html' and 'attachment' not in cdispo:
                                body = origin.get_payload(decode=True)
                                ctype = origin.get_content_type()

                                msg.attach(MIMEText(body, ctype.split('/')[1], 'utf-8'))
                                print('multi part mail %s -> %s ', (host, self.mail.to[0]))
                                client.hset(tag, host, msg.as_string())
                                client.expire(tag, 300)
                else:
                    body = origin.get_payload(decode=True)
                    print(host)
                    ctype = origin.get_content_type()

                    msg.attach(MIMEText(body, ctype.split('/')[1], 'utf-8'))
                    print('non multi part mail %s -> %s', (host, self.mail.to[0]))
                    client.hset(tag, host, msg.as_string())
                    client.expire(tag, 300)
        except:
            import traceback
            traceback.print_exc()
        return True

    def send(self, client, sender, receiver, mail):
        try:
            senderrs = client.sendmail(sender, receiver, mail)
            client.quit()
            return senderrs
        except:
            import traceback
            traceback.print_exc()
            raise Exception('send error!')

    def handle_schedule_mails(self):
        import time
        while True:
            keys = client.scan_iter(match='tag_*', count=20)
            for key in keys:
                data = client.hgetall(key)
                mail = right_judge(data)
                if mail:
                    host = "localhost"
                    server = smtplib.SMTP(host, port=25)
                    server.ehlo()
                    msg = email.message_from_string(mail.decode())
                    senderrs = server.sendmail(msg['From'], msg['TO'], mail)
                    print('send mail ', senderrs)
                    if not senderrs:
                        client.delete(key)
                    server.quit()
            time.sleep(3)