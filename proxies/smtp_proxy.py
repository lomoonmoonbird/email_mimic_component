# --*-- coding:utf-8 --*--

import logging, os, pickle, sys, threading, time, email, types, tempfile
from base64 import b64encode
from proxies import config
from inspect import getmembers, isfunction, isclass
from proxies import smtp_core


received_header		= 'Python SMTP Proxy'
smtpconfig			= None
mailaccounts		= {}
configFile 			= 'proxies/smtp_config.ini'
port				= 25
msgdir				= ''
sleeptime			= 30
waitafterpop		= 5
popchecktime		= 0
debuglevel			= 0
deleteonerror		= True

class MailAccount():
    """
    邮件账号 将配置里的用户实例化
    """
    def __init__(self):
        self.rsmtphost = None
        self.rsmtpport = 0
        self.rsmtpsecurity = 'none'
        self.rpophost = None
        self.rpopport = 995
        self.rpopssl = True
        self.rpopuser = None
        self.rpoppass = None
        self.rsmtpuser = None
        self.rsmtppass = None
        self.rPBS = False
        self.rpopcheckdelay = 60  # in sec
        self.localhostname = None
        self.returnpath = None
        self.useconfig = None


class Mail():
    """
    需要代理的邮件类
    """

    def __init__(self):
        self.msg = None
        self.to = []
        self.frm = ''

def get_mail_account(frm):
    """ 获取发送者email账号"""
    account = None
    if frm in mailaccounts.keys():
        account = mailaccounts[frm]
        if account.useconfig != None:
            if account.useconfig in mailaccounts.keys():
                account = mailaccounts[account.useconfig]
            else:
                return None
    return account

def encode_plain(user, password):
    """ 加密user password"""
    return b64encode("\0%s\0%s" % (user, password))


class SMTPProxy(smtp_core.SMTPServerInterface):
    """
    接收中转的邮件 每次SMTP连接建立的时候都会实例化，每次处理一个邮件
    """
    def __init__(self):
        self.mail = Mail()

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
        global msgdir, received_header

        self.mail.msg = (data)
        # account = get_mail_account(self.mail.frm)
        # if not account:
        #     return
        self.mail.msg = 'Receive: (' + received_header + ') ' + email.utils.formatdate() + '\n' +self.mail.msg
        for host, port in [("192.168.86.130", 25), ("192.168.86.129", 25)]:
            send_mail(self.mail, host, port)

def send_mail(mail: Mail, host, port, filename = None):
    import smtplib
    global popchecktime, mailaccounts, waitafterpop, debuglevel

    account = get_mail_account(mail.frm)
    # if not account:
    #     return False

    #发送邮件
    try:
        # if account.localhostname:
        #     server = smtplib.SMTP(account.rsmtphost, account.rsmtpport, account.localhostname)
        # else:
        #     server = smtplib.SMTP(account.rsmtphost, account.rsmtpport)
        server = smtplib.SMTP(host, port)
        server.set_debuglevel(debuglevel)
        server.ehlo()
        # if account.rsmtpuser:
        #     try:
        #         server.login(account.rsmtpuser, account.rsmtppass)
        #     except smtplib.SMTPAuthenticationError:
        #         code, resp = server.docmd("AUTH", "PLAIN" + encode_plain(account.rsmtpuser, account.rsmtppass))
        #         if code == 535:
        #             print("Authentication error")
        server.sendmail(mail.frm, mail.to, mail.msg)
        server.quit()

    except:
        import traceback
        print(sys.exc_info())
        traceback.print_exc()
        return False
    return True


def readConfig():
    """读取配置"""

    global smtpconfig, mailaccounts, port, msgdir, sleeptime, waitafterpop, debuglevel, deleteonerror
    if os.path.exists(configFile) == False:
        print('Configuration file "' + configFile + '" doesn''t exist. Exiting.')
        return False

    smtpconfig =config.Config()
    smtpconfig.read([configFile])

    port = smtpconfig.getint('config', 'port', port)
    sleeptime = smtpconfig.getint('config', 'sleeptime', sleeptime)
    waitafterpop = smtpconfig.getint('config', 'waitafterpop', waitafterpop)
    debuglevel = smtpconfig.getint('config', 'debuglevel', debuglevel)
    deleteonerror = smtpconfig.getboolean('config', 'deleteonerror', deleteonerror)
    distribute_hosts = smtpconfig.getboolean('config', 'distribute_hosts', deleteonerror)

    for s in smtpconfig.sections():
        if s not in ['logging', 'config']:
            account = MailAccount()

            account.useconfig = smtpconfig.get(s, 'use', account.useconfig)
            if account.useconfig != None:
                mailaccounts[s] = account
                continue

            account.rsmtphost = smtpconfig.get(s, 'smtphost', account.rsmtphost)
            account.rsmtpport = smtpconfig.getint(s, 'smtpport', account.rsmtpport)
            account.rsmtpsecurity = smtpconfig.get(s, 'smtpsecurity', account.rsmtpsecurity)
            account.rpophost = smtpconfig.get(s, 'pophost', account.rpophost)
            account.rpopport = smtpconfig.getint(s, 'popport', account.rpopport)
            account.rpopssl = smtpconfig.getboolean(s, 'popssl', account.rpopssl)
            account.rpopuser = smtpconfig.get(s, 'popusername', account.rpopuser)
            account.rpoppass = smtpconfig.get(s, 'poppassword', account.rpoppass)
            account.rPBS = smtpconfig.getboolean(s, 'popbeforesmtp', account.rPBS)
            account.rpopcheckdelay = smtpconfig.getint(s, 'popcheckdelay', account.rpopcheckdelay)
            account.rsmtpuser = smtpconfig.get(s, 'smtpusername', account.rsmtpuser)
            account.rsmtppass = smtpconfig.get(s, 'smtppassword', account.rsmtppass)
            account.localhostname = smtpconfig.get(s, 'localhostname', account.localhostname)
            account.returnpath = smtpconfig.get(s, 'returnpath', account.returnpath)

            if account.rsmtphost == None:
                return False
            if account.rPBS:
                if account.rpophost == None:
                    return False
                if account.rpopuser == None:
                    return False
                if account.rpoppass == None:
                    return False
            if account.rsmtpport == 0:
                if account.rsmtpsecurity == 'none' or account.rsmtpsecurity == 'tls':
                    account.rsmtpport = 25
                else:  # ssl
                    account.rsmtpport = 465

            mailaccounts[s] = account

    return True