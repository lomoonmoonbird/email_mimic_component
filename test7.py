import imaplib
import smtplib
import poplib
#
# server_socket = imaplib.IMAP4("mail8.moonmoonbird.com", 143)
# server_socket.login("mail1@moonmoonbird.com", "mail1")
#
# print(server_socket.__dict__)

# server_socket = poplib.POP3("mail.moonmoonbird.com")
# server_socket.user("mail1")
# server_socket.pass_("mail1")
# print(server_socket.__dict__)
# server_socket.close()
# print(server_socket.__dict__)

smtp_socket = smtplib.SMTP("mail7.moonmoonbird.com", 25)
smtp_socket.connect("mail7.moonmoonbird.com", 25)
smtp_socket.set_debuglevel(1)
smtp_socket.ehlo()
print(smtp_socket.ehlo())