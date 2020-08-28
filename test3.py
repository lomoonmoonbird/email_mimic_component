a = """
Return-Path: <jinpeng@moonmoonbird.com>
X-Original-To: jinpeng@moonmoonbird.com
Delivered-To: jinpeng@moonmoonbird.com
Received: from lproxy.moonmoonbird.com (unknown [192.168.6.67])
        by mail2.moonmoonbird.com (Postfix) with ESMTP id 47B0710DD77A;
        Tue, 11 Aug 2020 06:51:25 +0000 (UTC)
Tag: 4cbd19a3ac0472f2f20edabe635211a0
Receive: ( SMTP PROXY ) Tue, 11 Aug 2020 06:51:25 -0000
subject: test 1

test 1 1

"""

# b = [b'Return-Path: <jinpeng@moonmoonbird.com>\r\n', b'X-Original-To: jinpeng@moonmoonbird.com\r\n', b'Delivered-To: jinpeng@moonmoonbird.com\r\n', b'Received: from lproxy.moonmoonbird.com (unknown [192.168.6.67])\r\n', b'\tby mail2.moonmoonbird.com (Postfix) with ESMTP id 47B0710DD77A;\r\n', b'\tTue, 11 Aug 2020 06:51:25 +0000 (UTC)\r\n', b'Tag: 4cbd19a3ac0472f2f20edabe635211a0\r\n', b'Receive: ( SMTP PROXY ) Tue, 11 Aug 2020 06:51:25 -0000\r\n', b'subject: test 1\r\n', b'\r\n', b'test 1 1\r\n']
# num = 0
# for bb in b:
#     num += len(bb)
# print(num)
#
# c = [b'Return-Path: <jinpeng@moonmoonbird.com>\r\n', b'X-Original-To: jinpeng@moonmoonbird.com\r\n', b'Delivered-To: jinpeng@moonmoonbird.com\r\n', b'Received: from lproxy.moonmoonbird.com (unknown [192.168.6.67])\r\n', b'\tby mail2.moonmoonbird.com (Postfix) with ESMTP id 47B0710DD77A;\r\n', b'\tTue, 11 Aug 2020 06:51:25 +0000 (UTC)\r\n', b'Tag: 4cbd19a3ac0472f2f20edabe635211a0\r\n', b'Receive: ( SMTP PROXY ) Tue, 11 Aug 2020 06:51:25 -0000\r\n', b'subject: test 1\r\n', b'\r\n', b'test 1 1\r\n']
# num = 0
# for cc in c:
#     num += len(cc)
# print(num)
#
#
# d = b'Received: from mail8.moonmoonbird.com (mail8.moonmoonbird.com [192.168.7.78])\r\n\tby mail8.moonmoonbird.com (8.14.4/8.14.4/Debian-4.1ubuntu1.1) with ESMTP id 07LAdppp056785\r\n\tfor <15638749981@163.com>; Fri, 21 Aug 2020 18:39:52 +0800\r\nReceived: from 192.168.7.5\r\n        (SquirrelMail authenticated user susan)\r\n        by mail8.moonmoonbird.com with HTTP;\r\nFri, 21 Aug 2020 18:39:52 +0800\r\nMessage-ID: <05a92067b4e47e0348d45fd656c4e8e7.squirrel@mail8.moonmoonbird.com>\r\nDate: Fri, 21 Aug 2020 18:39:52 +0800\r\nSubject: \r\nFrom: susan@moonmoonbird.com\r\nTo: 15638749981@163.com\r\nUser-Agent: SquirrelMail/1.4.22\r\nMIME-Version: 1.0\r\nContent-Type: text/plain;charset=gb2312\r\nContent-Transfer-Encoding: 8bit\r\nX-Priority: 3 (Normal)\r\nImportance: Normal\r\n\r\n\xb7\xc5\xb4\xf3\xb7\xa2\xb7\xc5\r\n\r\n'
#
# print(d.decode('gb2312','ignore'))

e = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00 2.7.0 Authentication successful\r\n'
print(e.decode())