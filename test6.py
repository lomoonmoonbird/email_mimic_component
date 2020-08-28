import smtplib
import base64
from email.parser import HeaderParser
from email.header import decode_header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import email

mail = """
Received: from [192.168.7.158] (helo=[192.168.76.33])
        by moonmoonbird.com with esmtp (Exim 4.94)
        (envelope-from <jinpeng@moonmoonbird.com>)
        id 1kBVNn-001dkV-KE
        for jinpeng@comleader.com.cn; Thu, 27 Aug 2020 20:48:55 -0700
HOST:mail7.moonmoonbird.com
HOST:mail.moonmoonbird.com
Tag:tag_a2e8201f-275d-42ed-8fdc-d579b9c12fbb
MD5:c25ce38452ac3e668aa12a4cffec38e7
Accept-Language: ISO-8859-1,utf-8
Receive: ( SMTP PROXY ) Fri, 28 Aug 2020 03:48:54 -0000
Date: Fri, 28 Aug 2020 11:48:54 +0800
From: "jinpeng@moonmoonbird.com" <jinpeng@moonmoonbird.com>
To: =?GB2312?B?vfDF9A==?= <jinpeng@comleader.com.cn>
Subject: oooooooooooooo
X-Priority: 3
X-GUID: FB11FC2D-F498-484D-91A6-8265BFACDD29
X-Has-Attach: no
X-Mailer: Foxmail 7.2.18.95[cn]
Mime-Version: 1.0
Message-ID: <2020082811485287054014@moonmoonbird.com>
Content-Type: multipart/alternative;
        boundary="----=_001_NextPart518683371422_=----"

This is a multi-part message in MIME format.

------=_001_NextPart518683371422_=----
Content-Type: text/plain;
        charset="GB2312"
Content-Transfer-Encoding: base64

eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4DQoNCg0KDQpqaW5wZW5nQG1vb25tb29uYmlyZC5j
b20NCg==

------=_001_NextPart518683371422_=----
Content-Type: text/html;
        charset="GB2312"
Content-Transfer-Encoding: quoted-printable

<html><head><meta http-equiv=3D"content-type" content=3D"text/html; charse=
t=3DGB2312"><style>body { line-height: 1.5; }body { font-size: 14px; font-=
family: 'Microsoft YaHei UI'; color: rgb(0, 0, 0); line-height: 1.5; }</st=
yle></head><body>=0A<div><span></span>xxxxxxxxxxxxxxxxxxxxxxxxxxx</div>=0A=
<div><br></div><hr style=3D"width: 210px; height: 1px;" color=3D"#b5c4df" =
size=3D"1" align=3D"left">=0A<div><span><div style=3D"MARGIN: 10px; FONT-F=
AMILY: verdana; FONT-SIZE: 10pt"><div>jinpeng@moonmoonbird.com</div></div>=
</span></div>=0A</body></html>
------=_001_NextPart518683371422_=------
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
            break
else:
    print('adsas')