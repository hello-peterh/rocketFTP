#https://gist.github.com/bsquidwrd/17905d8fad10707901b7a0d7d14e7b37/6f354f99dc1e818e72dcecd7a057e765e3c73e36

import email
import imaplib
import os

SERVER = 'imap.gmail.com'
USERNAME = 'rocketFTP@gmail.com'
PASSWORD = 'rbcFTPtest$2018'

class FetchEmail():

    connection = None
    error = None

    def __init__(self, mail_server=SERVER, username=USERNAME, password=PASSWORD):
        print('Connected to: ' + mail_server)
        self.connection = imaplib.IMAP4_SSL(mail_server)
        self.connection.login(username, password)
        self.connection.select(readonly=True) #marks emails as read/unread

    def close_connection(self):
        self.connection.close()

    def save_attachment(self, msg, download_folder='/tmp'):

        att_path = "No attachment found."

        for part in msg.walk():
            if part.get_content_maintype() == 'multipart':
                continue

            if part.get('Content-Disposition') is None:
                continue
            
            filename = part.get_filename()
            att_path = os.path.join(download_folder, filename)

            if not os.path.isfile(att_path):
                outfile = open(att_path, 'wb')
                outfile.write(part.get_payload(decode=True))
                outfile.close()

            return att_path

    def fetch_unread_messages(self):

        emails = []
        (result, messages) = self.connection.search(None, 'UNSEEN')
        if result == "OK":
            for message in messages[0].decode('utf-8').split(' '):
                try:
                    ret, data = self.connection.fetch(message, '(RFC822)')
                except:
                    print("No new emails to read.")
                    self.close_connection()
                    exit()

                msg = email.message_from_string(data[0][1].decode('utf-8'))
                if 'content promotion' in msg['Subject']:
                    print(msg['Subject'])
                    if isinstance(msg,str) == False:
                        emails.append(msg)
                    response, data = self.connection.store(message, '+FLAGS', '\\Seen')
                
            return emails
        
        self.error = "Failed to retrieve emails."
        return emails

    def parse_email_address(self, email_address):
        return email.utils.parseaddr(email_address)
        

if __name__ == '__main__':
    f = FetchEmail(
        #mail_server = SERVER,
        #username=USERNAME,
        #password=PASSWORD
    )
    msgs = f.fetch_unread_messages()
    for m in msgs:
        file_location = f.save_attachment(
            msg=m,
            download_folder='/Users/peterhung/Personal Projects/autoFTP/tmp'
        )
        print(file_location)
    f.close_connection()