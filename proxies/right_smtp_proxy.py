# --*-- coding:utf-8 --*--

import logging, os, pickle, sys, threading, time, email, types, tempfile
from base64 import b64encode
from proxies.config import readConfig
from inspect import getmembers, isfunction, isclass
from proxies import right_smtp_core
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

CONFIG_PATH = 'proxies/right_smtp_config.ini'
smtpcfg = readConfig(CONFIG_PATH)


class Mail():
    """
    需要代理的邮件类
    """

    def __init__(self):
        self.msg = None
        self.to = []
        self.frm = ''


def encode_plain(user, password):
    """ 加密user password"""
    return b64encode("\0%s\0%s" % (user, password))


class SMTPProxy(right_smtp_core.SMTPServerInterface):
    """
    接收中转的邮件 每次SMTP连接建立的时候都会实例化，每次处理一个邮件
    """
    def __init__(self):
        self.mail = Mail()
        self.mail_center = []

    def mail_from(self, mail):
        """
        邮件发送人部分
        :return:
        """
        self.mail.frm = right_smtp_core.stripAddress(mail)

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
        self.mail_center.append(self.mail.msg)
        print('---------------------------------------')
        print(len(self.mail_center))
        print('-----------------------------------------')
        print(self.mail_center[0], self.mail.frm, self.mail.to)

def send_mail(mail: Mail, host, port, filename = None):
    import smtplib
    #发送邮件
    try:
        server = smtplib.SMTP(host, port)
        server.set_debuglevel(smtpcfg['config'].debuglevel)
        server.ehlo()
        server.sendmail(mail.frm, mail.to, mail.msg)
        server.quit()

    except:
        import traceback
        traceback.print_exc()
        return False
    return True



