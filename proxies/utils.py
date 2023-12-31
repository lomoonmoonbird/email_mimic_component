"""
    Implementation of the PyCIRCLeanMail module.
    Sanitize emails before being fetched by the user.
"""

import email, re, imaplib, time, hashlib, hmac
from io import BytesIO
import logging, logging.handlers, time
import os
# from kittengroomer_email import KittenGroomerMail

"""
    Helpers for the modules (PyCIRCLeanMail & MISP)
"""

def parse_ids(str_ids):
    """ Convert string of ids to a list of ids
        str_ids - ids of format "1:6" or "1,3:5" or "1,4"
    If str_ids = "1:6", return (1,2,3,4,5,6).
    If str_ids = "1,3:5", return (1,3,4,5).
    If str_ids = "1,4", return (1,4).
    """

    ids = []
    raw_ids = str_ids.split(',')

    for s in raw_ids:
        if ':' in s:
            (start, end) = s.split(':')
            print(start, end)
            [ids.append(i) for i in range(int(start), int(end)+1)]
        else:
            ids.append(int(s))

    return ids

Fetch = re.compile(r'(?P<tag>[A-Z0-9]+)'
    r'(\s(UID))?'
    r'\s(FETCH)'
    r'\s(?P<ids>[0-9:,]+)'
    r'\s(?P<flags>.*)', flags=re.IGNORECASE)

# Default Quarantine folder
QUARANTINE_FOLDER = 'Quarantine'

# Sanitizer header and values
CIRCL_SIGN = 'X-CIRCL-Sanitizer'
VALUE_ORIGINAL = 'Original'
VALUE_SANITIZED= 'Sanitized'
VALUE_ERROR= 'Error'
# Proxy header to verify email integrity
PROXY_SIGN = 'X-Proxy-Sign'

# Message data used to get the flags and sanitizer header
MSG_DATA_FS = '(FLAGS BODY.PEEK[HEADER.FIELDS (' + CIRCL_SIGN + ')])'
# Message data used to get the entire mail
MSG_DATA = 'BODY.PEEK[]'

def process(client):
    """ Apply the PyCIRCLeanMail module if the request match with a Fetch request
        client - Connection object
    """
    request = client.request
    conn_server = client.server_socket
    folder = client.current_folder
    key = client.key

    # Only sanitize emails in the Inbox
    if ("QUARANTINE" in folder.upper()) or ("SENT" in folder.upper()):
            print("Don't need to sanitize in the folder:", folder)
            return

    uidc = True if (('UID' in request) or ('uid' in request)) else False

    match = Fetch.match(request)
    if not match: return # Client discovers new emails (presence of '*' key)
    ids = match.group('ids')

    if ids.isdigit():
        # Only one email fetched
        process_email(ids, conn_server, folder, uidc, key)
    else:
        # Multiple emails are fetched (ids format: [0-9,:])
        for id in parse_ids(ids):
            process_email(str(id), conn_server, folder, uidc, key)

def process_email(id, conn_server, folder, uidc, key):
    """ Sanitize, if necessary, an email.
        id - String containing the id of the email to fetch;
        conn_server - imaplib connection to the server;
        folder - Current folder of the client;
        uidc - True if command contains UID flag
        key - key used to verify integrity of email
    If the email is not sanitized yet, make a sanitized copy in the same folder
    and an unsanitized copy if the Quarantine folder. The original email is deleted.
    """

    conn_server.select(folder)

    if has_CIRCL_signature(id, conn_server, uidc):
        return
    print('Email not sanitized')

    #   -- No CIRCL signature or incorrect value --
    bmail = fetch_entire_email(id, conn_server, uidc)
    if not bmail:
        return
    mail = email.message_from_bytes(bmail)

    # Get the DATE of the email
    date_str = mail.get('Date')
    date = imaplib.Internaldate2tuple(date_str.encode()) if date_str else imaplib.Time2Internaldate(time.time())

    # Get the payload and hash
    digest_original = hash_payload(get_payload(mail), key)

    # Sanitize the email
    content = sanitize_email(bmail)
    # content = bmail.decode()
    if not content:
        return

    # Copy of the sanitized email
    smail = email.message_from_bytes(content.getvalue())
    digest_sanitized = hash_payload(get_payload(smail), key)
    append_email(conn_server, smail, digest_sanitized, VALUE_SANITIZED, date, folder)

    # Copy of the original email in the Quarantine folder
    append_email(conn_server, mail, digest_original, VALUE_ORIGINAL, date, QUARANTINE_FOLDER)

    # Delete original
    conn_server.uid('STORE', id, '+FLAGS', '(\Deleted)') if uidc else conn_server.store(id, '+FLAGS', '(\Deleted)')
    conn_server.expunge()

def has_CIRCL_signature(id, conn_server, uidc):
    """ Return False if the email with the given id has not been sanitized yet """

    result, response = conn_server.uid('fetch', id, MSG_DATA_FS) if uidc else conn_server.fetch(id, MSG_DATA_FS)

    if result == 'OK' and response[0]:
        try:
            [(flags, signature), ids] = response
        except ValueError:
            # Not correct response
            return True

        if (CIRCL_SIGN.encode() in signature) and (VALUE_SANITIZED.encode() in signature):
            print('Already sanitized')
            return True

    return False

def fetch_entire_email(id, conn_server, uidc):
    """ Return the raw_email in bytes """
    result, response = conn_server.uid('fetch', id, MSG_DATA) if uidc else conn_server.fetch(id, MSG_DATA)

    if result == 'OK' and response != [b'The specified message set is invalid.'] and response != [None]:
        bmail = response[0][1]
    else:
        return

    return bmail

def sanitize_email(bmail):
    """ Sanitize the raw email (in bytes) using the PyCIRCLeanMail module """
    # t = KittenGroomerMail(bmail)
    # m = t.process_mail()
    # return BytesIO(m.as_bytes())
    return BytesIO(bmail)

def append_email(conn_server, mail, proxy_value, circl_value, date, folder):
    """ Append the email on the server """
    mail.add_header(CIRCL_SIGN, circl_value)
    mail.add_header(PROXY_SIGN, proxy_value)
    conn_server.append(folder, '', date, str(mail).encode())

def get_payload(mail):
    """ Return the payload of the given email """
    res = ''
    if mail.is_multipart():
        for payload in mail.get_payload():
            res += payload.get_payload()
    else:
        res = mail.get_payload()

    return res

def hash_payload(payload, key):
    """ Hash the payload """
    return hmac.new(str(key).encode('utf-8'), str(payload).encode('utf-8'), hashlib.sha1).hexdigest()


class Logging:
    """ Wrapper class for the logging subsystem. This class wraps the
        initialization of the logging subsystem and provides convenience
        methods for printing log, error and warning messages to a
        logfile and to the console.
    """
    # some logging defaults
    _logFile = 'log.log'
    _logSize = 1000000
    _logCount = 10
    _logLevel = logging.INFO
    _isinit = False

    def __init__(self, logFile=_logFile, logSize=_logSize, logCount=_logCount, logLevel=_logLevel):
        """Init the logging system.
        """

        if self._isinit == True:    return

        self.logger = logging.getLogger('logging')
        logfp = logging.handlers.RotatingFileHandler(logFile, maxBytes=logSize, backupCount=logCount)
        logformatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        logfp.setFormatter(logformatter)
        self.logger.addHandler(logfp)
        self.logLevel = logLevel
        logfp.setLevel(logLevel)
        self.logger.setLevel(logLevel)
        self._isinit = True

    def log(self, msg):
        """Print a log message with level INFO.
        """

        try:
            if self.logLevel <= logging.INFO:
                print("(" + time.ctime(time.time()) + ") " + msg)
                if self._isinit:
                    self.logger.info(msg)
        except:
            pass

    def logdebug(self, msg):
        """Print a log message with level DEBUG.
        """

        try:
            if self.logLevel <= logging.DEBUG:
                print("DEBUG: (" + time.ctime(time.time()) + ") " + msg)
                if self._isinit:
                    self.logger.debug(msg)
        except:
            pass

    def logerr(self, msg):
        """Print a log message with level ERROR.
        """

        try:
            if self.logLevel <= logging.ERROR:
                print("ERROR: (" + time.ctime(time.time()) + ") " + msg)
                if self._isinit:
                    self.logger.error(msg)
        except:
            pass

    def logwarn(self, msg):
        """Print a log message with level WARNING.
        """

        try:
            if self.logLevel <= logging.WARNING:
                print("Warning: (" + time.ctime(time.time()) + ") " + msg)
                if self._isinit:
                    self.logger.warning(msg)
        except:
            pass