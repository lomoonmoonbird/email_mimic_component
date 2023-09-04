import smtplib
import poplib
from email.mime.text import MIMEText
from email.header import Header
import email
import base64
from email.header import decode_header

# content = 'Received: from [192.168.6.99] (helo=[192.168.76.33])\r\n\tby moonmoonbird.com with esmtpa (Exim 4.94)\r\n\t(envelope-from <jinpeng@moonmoonbird.com>)\r\n\tid 1kAA3x-0000Zr-BJ\r\n\tfor jinpeng@comleader.com.cn; Mon, 24 Aug 2020 03:50:53 -0700\r\nContent-Type: text/plain; charset="utf-8"\r\nMIME-Version: 1.0\r\nContent-Transfer-Encoding: base64\r\nFrom: jinpeng@moonmoonbird.com\r\nTo: jinpeng@comleader.com.cn\r\nTag: 903c5a9755c6b0f5e9d46407587c780c\r\nAccept-Language: zh-CN\r\nAccept-Charset: ISO-8859-1,utf-8\r\nMessage-Id: <E1kAA3x-0000Zr-BJ@moonmoonbird.com>\r\nDate: Mon, 24 Aug 2020 03:50:53 -0700\r\n\r\nQ29udGVudC1UeXBlOiB0ZXh0L3BsYWluOyBjaGFyc2V0PSJ1dGYtOCINCk1JTUUtVmVyc2lvbjog\r\nMS4wDQpDb250ZW50LVRyYW5zZmVyLUVuY29kaW5nOiBiYXNlNjQNCkZyb206ID0/dXRmLTg/cT9q\r\naW5wZW5nPz0NClRvOiA9P3V0Zi04P3E/amlucGVuZz89DQpTdWJqZWN0OiA9P3V0Zi04P3E/UHl0\r\naG9uX1NNVFBfamlucGVuZy0zPz0NCg0KVUhsMGFHOXVJSE5sYm1RZ2RHVnpkRE11TGk0PQ=='
content = 'Received: from [192.168.76.33] (unknown [192.168.6.99])\r\n\tby mail.moonmoonbird.com (Postfix) with ESMTPA id 1870510DD77B\r\n\tfor <jinpeng@comleader.com.cn>; Mon, 24 Aug 2020 11:55:48 +0000 (UTC)\r\nTag: d85bd8b0d15fbd7481f946ca538f146f\r\nAccept-Language: ISO-8859-1,utf-8\r\nAccept-Language: ISO-8859-1,utf-8\r\nReceive: ( SMTP PROXY ) Mon, 24 Aug 2020 11:55:47 -0000\r\nContent-Type: text/plain; charset="utf-8"\r\nMIME-Version: 1.0\r\nContent-Transfer-Encoding: base64\r\nFrom: =?utf-8?q?jinpeng?=\r\nTo: =?utf-8?q?jinpeng?=\r\nSubject: =?utf-8?q?love_7777777?=\r\n\r\namlucGVuZyA3Nzc3Nzc='
msg = email.message_from_string(content)

# if msg.is_multipart():
#     for payload in msg.get_payload():
#         # if payload.is_multipart(): ...
#         # print (payload.get_payload(), '@@@@@@')
#         pass
# else:
#     mytext = base64.urlsafe_b64decode(msg.get_payload().encode('UTF-8'))
#     print(mytext)
#     print(msg.get_payload(decode=True))
#     print (msg.get_content_type())
#     print(msg.keys())
#     print(decode_header(msg['Subject']), type(msg['Subject']))
#
#     print(decode_header(msg['Receive']), type(msg['Receive']))
#     print(msg['Tag'])
# body = ""
# b = msg
# if b.is_multipart():
#     for part in b.walk():
#         ctype = part.get_content_type()
#         cdispo = str(part.get('Content-Disposition'))
#
#         # skip any text/plain (txt) attachments
#         if ctype == 'text/plain' and 'attachment' not in cdispo:
#             print(1)
#             body = part.get_payload(decode=True)  # decode
#             break
# # not multipart - i.e. plain text, no attachments, keeping fingers crossed
# else:
#
#     # for part in b.walk():
#     #     print(part)
#     ctype = msg.get_content_type()
#     print(ctype)
#     print(2)
#     body = b.get_payload(decode=True)
# print(body)

from email.parser import HeaderParser
from email.header import decode_header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

body = msg.get_payload(decode=True)
ctype = msg.get_content_type()
msg = MIMEMultipart()
msg['Subject'] = msg['Subject']
msg['Receive'] = msg['Receive']
msg['From'] = "asds"
msg['To'] = "sads"
msg['reply-to'] = ""
msg['X-Priority'] = ""
msg['CC'] = ""
msg['BCC'] = ""
msg['Tag'] = msg['Tag']
msg['MD5'] = msg['MD5']
msg['Return-Receipt-To'] = "asds"
msg["Accept-Language"] = "zh-CN"
msg.preamble = 'Event Notification'
msg["Accept-Charset"] = "ISO-8859-1,utf-8"
msg.attach(MIMEText(body, ctype.split('/')[1], 'utf-8'))
print('self.mail.to[0]self.mail.to[0]self.mail.to[0]', "self.mail.to[0]")
print('type   ', type(msg.as_string()))
print(msg.as_string())
