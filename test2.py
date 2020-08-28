import smtplib
import poplib
from email.mime.text import MIMEText
from email.header import Header

host = "mail8.moonmoonbird.com"

FROM = "mail2@moonmoonbird.com"
TO = "jinpeng@comleader.com.cn"
message = MIMEText("""如果需要会员资料用于后续发送用的,建议邮箱地址进行验证;
----------
1 用户不存在 代码550
2,如sohu的发件人封锁未解,也打回.代码553
3. 用户停用 代码550
4. 挨过滤系统拒绝 代码543,21cn最多,基本上过不了.
5. yahoo的转发错误,用户没有账号,估计是有用户名,代码554;
6. hotmail的用户的收件箱不可用,可能停用,代码550;
7. yahoo转发错误,用户的信箱挨停用.代码554;
8. 国外的过滤系统对内容过滤打回代码553;
9. 万网的收件人:553 RP:RDN     收件人被拒绝，用户不存在或禁止转发
10. 万网进行内容过滤,554 Spam content detected;
11. 台湾的服务器不可达,500;
* bjsss.net设置拒绝接收,代码550;

der日志分析
撒大声地所是撒是撒飒飒的是
* yahoo的会挨用户投诉而拒绝;
conversation with mail.fdf.com.cn[61.145.69.85] timed out while sending end of data -- message may be sent more than once:估计使用了内部或标题判断规则,不同用户重复(估计就算一次重复)内容会被拒绝.
163.com:邮件正文带有垃圾邮件特征或发送环境缺乏规范性，被临时拒收
kaac@keytj.com:前后两次发信间隔小于阀值 (300秒)""", 'plain', 'utf-8')
# message['From'] = Header("mail2", 'utf-8')  # 发送者
# message['To'] = Header("mail1", 'utf-8')  # 接收者
message['From'] = FROM
message['To'] = TO
message['Subject'] = Header('postfix如何设置ccccc', 'utf-8')
message['TAG'] = "tag_jinpeng"
message['HOST'] = 'mail8.moonmoonbrid.com'

server = smtplib.SMTP(host, port=25)
server.set_debuglevel(1)
a = server.ehlo()
server.login("mail2", "mail2")

b = server.sendmail(FROM, TO, message.as_string())
# print(server.verify("52071552@qq.com"))
print(b)
server.quit()
print ("Email Send")