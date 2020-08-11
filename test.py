import smtplib
import poplib
from email.mime.text import MIMEText
from email.header import Header

host = "lproxy.example.com"
server = smtplib.SMTP(host, port=9000)
FROM = "jinpeng@example.com"
TO = "lomoonmoonbird@gmaila.com"
message = MIMEText('Python send test3...', 'plain', 'utf-8')
message['From'] = Header("root", 'utf-8')  # 发送者
message['To'] = Header("jinpeng", 'utf-8')  # 接收者
message['Content-Transfer-Encoding'] = 'plain'
subject = 'Python SMTP 发送测试3'
message['Subject'] = Header(subject, 'utf-8')

# data = b"FROM: jinpeng@example.com\r\n"
# data += b"52071552@qq.com\r\n"
# data += b"Content-Transfer-Encoding: plain\r\n"
# data += b"Subject: aaaaa\r\n"
# data += b"bbbbbbbbbbbbbbbb"
# server.send(data)
# a = server.docmd("HELO")
# b = server.docmd("AUTH LOGIN")
# c = server.docmd("amlucGVuZw==")
# d = server.docmd("amlucGVuZw==")
# e = server.docmd("MAIL TO:", "jinpeng@example.com")
# f = server.docmd("RCPT TO:", "52071552@qq.com")
# g = server.docmd("DATA")
# h = server.docmd("DATA",args="aaaa\r\n.\r\n")
# print(a, b, c,d,e,f)
# server.login("52071552@qq.com", "keydwqlnyixlbhac")
server.login("jinpeng", "jinpeng")
server.ehlo()
server.sendmail(FROM, TO, message.as_string())
# print(server.verify("52071552@qq.com"))
server.quit()
print ("Email Send")



# from email.mime.text import MIMEText
# msg = MIMEText('hello, send by Python...', 'plain', 'utf-8')
# # 输入Email地址和口令:
# from_addr = "jinpeng@example.com"
# # 输入收件人地址:
# to_addr = "52071552@qq.com"
# # 输入SMTP服务器地址:
# smtp_server = "mail.example.com"
#
# import smtplib
# server = smtplib.SMTP(smtp_server, 25) # SMTP协议默认端口是25
# server.set_debuglevel(1)
# # server.login(from_addr, "PengKim@89527")
# server.sendmail(from_addr, [to_addr], msg.as_string())
# server.quit()


# import smtplib
# from email.mime.text import MIMEText
# from email.header import Header
#
# sender = 'root@example.com'
# receivers = ['jinpeng@example.com']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
#
# # 三个参数：第一个为文本内容，第二个 plain 设置文本格式，第三个 utf-8 设置编码
# message = MIMEText('Python 邮件发送测试...', 'plain', 'utf-8')
# message['From'] = Header("菜鸟教程", 'utf-8')  # 发送者
# message['To'] = Header("测试", 'utf-8')  # 接收者
#
# subject = 'Python SMTP 邮件测试'
# message['Subject'] = Header(subject, 'utf-8')
#
# try:
#     smtpObj = smtplib.SMTP('192.168.86.136')
#     smtpObj.sendmail(sender, receivers, message.as_string())
#     print("邮件发送成功")
# except smtplib.SMTPException:
#     import traceback
#     traceback.print_exc()
#     print( "Error: 无法发送邮件")


# server_socket = poplib.POP3("mail.example.com")
# server_socket.user("jinpeng")
# server_socket.pass_("jinpeng")
# print(server_socket.list())

# import asyncio
# def a():
#     print ('hi')
#
# def b():
#     print('hello')
#
# loop = asyncio.get_event_loop()
# loop.run_in_executor(None, a)
#
# from email.utils import make_msgid
# print(make_msgid())
#
# import imaplib
#
# # s = imaplib.IMAP4("localhost", 7000)
# s = imaplib.IMAP4("lproxy.example.com", 143)
# s.login("jinpeng", "jinpeng")
# s.login("jinpeng", "jinpeng")
# print(s.status('inbox', '(MESSAGES RECENT UIDNEXT UIDVALIDITY UNSEEN)'))