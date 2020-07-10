#!bin/python
# --*-- coding: utf-8 --*--

from aiohttp.web import Response
import json
import smtplib
from socket import gaierror

class Proxy():

    def __init__(self):
        pass

    @staticmethod
    async def send_mail(request):
        data = await request.json()

        port = 25
        smtp_server = "172.17.0.5"
        username = "jinpeng@psyguanling.com"
        password = "jinpeng"
        sender = "susan@psyguanling.com"
        receiver = "jinpeng@psyguanling.com"

        message = f"""
            Subject: Hi test
            To: {receiver}
            From: {sender}
            This is my test email
        """

        try:
            with smtplib.SMTP(smtp_server, port) as server:
                server.ehlo()
                # server.starttls()
                # server.login(username, password)
                server.sendmail(sender, receiver, message)
        except (gaierror, ConnectionRefusedError):
            print('Failed to connect to the server. Bad connection settings?')
        except smtplib.SMTPServerDisconnected:
            print('Failed to connect to the server. Wrong user/password?')
        except smtplib.SMTPException as e:
            print('SMTP error occurred: ' + str(e))
        return Response(body=json.dumps({"hi":'fff'}))
