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

            try:
                print('creating..', host ,port)
                server = smtplib.SMTP(host, port)
                server.connect(host, port)
                server.ehlo()
                server.set_debuglevel(smtpcfg['config'].debuglevel)
                server.ehlo()
                self.mail_clients.append(server)
            except:
                print("problemn:",  host, port)
                import traceback
                traceback.print_exc()
                # server.close()

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
        import uuid
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        from email.header import Header


        self.mail.msg = (data)
        random_uuid = str(uuid.uuid4())
        md = hashlib.md5()
        md.update(self.mail.msg.encode('utf-8'))
        self.mail.msg = 'Receive: ( SMTP PROXY ) ' + email.utils.formatdate() + '\r\n' + self.mail.msg
        self.mail.msg = 'Accept-Language: ISO-8859-1,utf-8' + '\r\n' + self.mail.msg
        self.mail.msg = 'MD5:' + md.hexdigest() + '\r\n' + self.mail.msg
        self.mail.msg = 'Tag:' + 'tag_' + random_uuid + '\r\n' + self.mail.msg


        origin = email.message_from_string(self.mail.msg)

        # if origin.is_multipart():
        #     for part in origin.walk():
        #         ctype = part.get_content_type()
        #         cdispo = str(part.get('Content-Disposition'))
        #
        #         if ctype == 'text/plain' and 'attachment' not in cdispo:
        #             body = part.get_payload(decode=True)  # decode
        #             break
        # else:

        # body = origin.get_payload(decode=True)
        # ctype = origin.get_content_type()
        # msg = MIMEMultipart()
        # msg['Subject'] = origin['Subject']
        # msg['Receive'] = origin['Receive']
        # msg['From'] = self.mail.frm
        # msg['To'] = self.mail.to[0]
        # msg['reply-to'] = ""
        # msg['X-Priority'] = ""
        # msg['CC'] = ""
        # msg['BCC'] = ""
        # msg['Tag'] = random_uuid
        # msg['MD5'] = md.hexdigest()
        # msg['Return-Receipt-To'] = self.mail.frm
        # msg["Accept-Language"] = "zh-CN"
        # msg.preamble = 'Event Notification'
        # msg["Accept-Charset"] = "ISO-8859-1,utf-8"
        # msg.attach(MIMEText(body, ctype.split('/')[1], 'utf-8'))
        # print('mail -> ', self.mail.to[0])


        # msg = MIMEMultipart()
        # msg['Subject'] = origin.get('Subject', '')
        # msg['From'] = self.mail.frm
        # msg['To'] = self.mail.to[0]
        # msg['reply-to'] = ""
        # msg['X-Priority'] = ""
        # msg['CC'] = ""
        # msg['BCC'] = ""
        # msg['Tag'] = random_uuid
        # msg['MD5'] = md.hexdigest()
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
        with ThreadPoolExecutor(max_workers=10) as e:
            for client in self.mail.mail_clients:
                self.mail.msg = 'HOST:' + client._host + '\r\n' + self.mail.msg
                # msg['HOST'] = client._host
                obj = e.submit(self.send, client, self.mail.frm, self.mail.to[0], self.mail.msg)
                obj_list.append(obj)
                for future in as_completed(obj_list):
                    senderrs = future.result()
                    print(senderrs, 'senderrrrrrrr')
            return True

    def send(self, client, sender, receiver, mail):
        senderrs = None
        try:
            senderrs = client.sendmail(sender, receiver, mail)
            client.quit()
            return senderrs
        except:
            import traceback
            traceback.print_exc()
            raise Exception('send errror',senderrs, sender,receiver,client.__dict__)



