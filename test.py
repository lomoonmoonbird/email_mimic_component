import smtplib

host = "192.168.86.129"
server = smtplib.SMTP(host)
FROM = "root"
TO = "jinpeng"
MSG = "Subject: Test email python\n\nBody of your message!"
server.sendmail(FROM, TO, MSG)

server.quit()
print ("Email Send")