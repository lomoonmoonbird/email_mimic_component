# --*-- coding:utf-8 --*--

import logging, os, pickle, sys, threading, time, email, types, tempfile
from base64 import b64encode
from proxies.config import readConfig
from inspect import getmembers, isfunction, isclass
from proxies import smtp_core
from collections import defaultdict
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
            print(host,port)
            server = smtplib.SMTP(host, port)
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
        "250-AUTH PLAIN",
        "250-AUTH=PLAIN",
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
        self.mail.frm = smtp_core.stripAddress(mail)

    def rcpt_to(self, mail):
        """
        邮件收件人
        :param mail:
        :return:
        """
        self.mail.to.append(mail.split(":")[1].strip())

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
        self.mail.msg = (data)
        self.mail.msg = 'Receive: ( SMTP PROXY ) ' + email.utils.formatdate() + '\n' +self.mail.msg
        md = hashlib.md5()
        md.update(self.mail.msg.encode('utf-8'))
        self.mail.msg = 'Tag: ' +  md.hexdigest() + '\n' +self.mail.msg

        # hosts = [(hp.split(':')[0], hp.split(':')[1]) for hp in smtpcfg['config'].distribute_hosts.split(",")]
        obj_list = []
        # with ThreadPoolExecutor(max_workers=3) as e:
        #     for host, port in hosts:
        #         obj = e.submit(send_mail, self.mail, host, port)
        #         obj_list.append(obj)
        #
        #     for future in as_completed(obj_list):
        #         data = future.result()
        #         print(data)

        with ThreadPoolExecutor(max_workers=3) as e:
            for client in self.mail.mail_clients:
                obj = e.submit(self.send, client, self.mail)
                obj_list.append(obj)

            for future in as_completed(obj_list):
                data = future.result()
                print(data)

    def send(self, client, mail):
        try:
            client.sendmail(mail.frm, mail.to, mail.msg)
            client.quit()
        except:
            import traceback
            traceback.print_exc()
            return False
        return True

# def send_mail(mail: Mail, host, port, filename = None):
#     import smtplib
#     #发送邮件
#     try:
#         server = smtplib.SMTP(host, port)
#         server.set_debuglevel(smtpcfg['config'].debuglevel)
#         server.ehlo()
#         server.sendmail(mail.frm, mail.to, mail.msg)
#         server.quit()
#
#     except:
#         import traceback
#         traceback.print_exc()
#         return False
#     return True



