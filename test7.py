import imaplib
import smtplib
import poplib
#
# server_socket = imaplib.IMAP4("mail10.moonmoonbird.com", 143)
# server_socket.login("mail1@moonmoonbird.com", "mail1")
#
# print(server_socket.__dict__)
#
# server_socket = poplib.POP3("mail.moonmoonbird.com")
# server_socket.user("mail14@moonmoonbird.com")
# server_socket.pass_("mail14")
# print(server_socket.__dict__)
# server_socket.close()
# print(server_socket.__dict__)

smtp_socket = smtplib.SMTP("mail.moonmoonbird.com", 25)
smtp_socket.connect("mail.moonmoonbird.com", 25)
smtp_socket.set_debuglevel(1)
# smtp_socket.ehlo()
smtp_socket.login("mail1@moonmoonbird.com", "mail1")
# smtp_socket.sendmail('mail7@moonmoonbird.com','mail2@moonmoonbird.com', 'adadsad')
# print(smtp_socket.ehlo())