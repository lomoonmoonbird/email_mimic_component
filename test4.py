import smtplib
import poplib
from email.mime.text import MIMEText
from email.header import Header

# host = "mail7.moonmoonbird.com"
# server = smtplib.SMTP(host, port=25)
# FROM = "jinpeng@moonmoonbird.com"
# TO = "52071552@qq.com"
# message = MIMEText('Python send test3...', 'plain', 'utf-8')
# message['Content-Transfer-Encoding'] = 'plain'
# subject = 'Python SMTP 发送测试3'
# message['Subject'] = Header(subject, 'utf-8')
#
# a = server.ehlo()
# print(a)
# b = server.sendmail(FROM, TO, message.as_string())
# print(b)
# server.quit()
# print ("Email Send")



server = smtplib.SMTP("mail.moonmoonbird.com", 25)
server.ehlo()
server.connect("mail.moonmoonbird.com", 25)
server.set_debuglevel(1)