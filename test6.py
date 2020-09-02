import smtplib
import base64
from email.parser import HeaderParser
from email.header import decode_header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import email

mail = """
X-Original-To: mail1@moonmoonbird.com

Delivered-To: mail1@moonmoonbird.com

Received: from [192.168.76.33] (unknown [192.168.6.29])

by mail.moonmoonbird.com (Postfix) with ESMTP id ED0BF107AB5D

for <mail1@moonmoonbird.com>; Wed,  2 Sep 2020 01:06:47 +0000 (UTC)

HOST:mail.moonmoonbird.com

Tag:tag_d19c43b2-f108-4853-bf25-bcdc26f5897e

MD5:a99f80d6d384a55315adaf7ddb48e928

Accept-Language: ISO-8859-1,utf-8

Receive: ( SMTP PROXY ) Wed, 02 Sep 2020 01:06:47 -0000

Date: Wed, 2 Sep 2020 09:06:47 +0800

From: "mail2@moonmoonbird.com" <mail2@moonmoonbird.com>

To: mail1 <mail1@moonmoonbird.com>

Subject: aaaaaa

X-Priority: 3

X-GUID: 1E19EEF5-BD40-4F6E-BF3D-1111692FFF3E

X-Has-Attach: no

X-Mailer: Foxmail 7.2.18.95[cn]

Mime-Version: 1.0

Message-ID: <202009020906417943700@moonmoonbird.com>

Content-Type: multipart/alternative;

boundary="----=_001_NextPart027704675633_=----"



This is a multi-part message in MIME format.



------=_001_NextPart027704675633_=----

Content-Type: text/plain;

charset="us-ascii"

Content-Transfer-Encoding: base64



DQpiYmJiYmINCg0KDQptYWlsMkBtb29ubW9vbmJpcmQuY29tDQo=



------=_001_NextPart027704675633_=----

Content-Type: text/html;

charset="us-ascii"

Content-Transfer-Encoding: quoted-printable



<html><head><meta http-equiv=3D"content-type" content=3D"text/html; charse=

t=3Dus-ascii"><style>body { line-height: 1.5; }body { font-size: 14px; fon=

t-family: 'Microsoft YaHei UI'; color: rgb(0, 0, 0); line-height: 1.5; }</=

style></head><body>=0A<div><span></span><br></div>=0A<div>bbbbbb</div><hr =

style=3D"width: 210px; height: 1px;" color=3D"#b5c4df" size=3D"1" align=3D=

"left">=0A<div><span><div style=3D"MARGIN: 10px; FONT-FAMILY: verdana; FON=

T-SIZE: 10pt"><div>mail2@moonmoonbird.com</div></div></span></div>=0A</bod=

y></html>

------=_001_NextPart027704675633_=------
"""
origin = email.message_from_string(mail)
ctype = origin.get_content_type()


msg = MIMEMultipart()
msg['Subject'] = origin['Subject']
msg['Receive'] = origin['Receive']
msg['From'] = origin['From']
msg['To'] = origin['From']
msg['reply-to'] = ""
msg['X-Priority'] = ""
msg['CC'] = ""
msg['BCC'] = ""
msg['Tag'] = origin['Tag']
msg['MD5'] = origin['MD5']
msg['Return-Receipt-To'] = origin['From']
msg["Accept-Language"] = "zh-CN"
msg.preamble = 'Event Notification'
msg["Accept-Charset"] = "ISO-8859-1,utf-8"
msg.attach(MIMEText("""<html><head><meta http-equiv=3D"content-type" content=3D"text/html; charse=
t=3DGB2312"><style>body { line-height: 1.5; }body { font-size: 14px; font-=
family: 'Microsoft YaHei UI'; color: rgb(0, 0, 0); line-height: 1.5; }</st=
yle></head><body>=0A<div><span></span>xxxxxxxxxxxxxxxxxxxxxxxxxxx</div>=0A=
<div><br></div><hr style=3D"width: 210px; height: 1px;" color=3D"#b5c4df" =
size=3D"1" align=3D"left">=0A<div><span><div style=3D"MARGIN: 10px; FONT-F=
AMILY: verdana; FONT-SIZE: 10pt"><div>jinpeng@moonmoonbird.com</div></div>=
</span></div>=0A</body></html>""", ctype.split('/')[1], 'utf-8'))


print(type(origin))
if msg.is_multipart():
    print('multipart')
    for part in msg.walk():
        ctype = part.get_content_type()
        cdispo = str(part.get('Content-Disposition'))
        print('ctype', ctype)
        if ctype == 'text/plain' and 'attachment' not in cdispo:
            body = part.get_payload(decode=True)  # decode
            print(body)
else:
    print('adsas')