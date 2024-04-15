import smtplib
from email.message import EmailMessage

def send(attachments=""):
   # Create the container email message.
   msg = EmailMessage()
   msg['Subject'] = 'REPORT: Customers added last 7 days'
   # me == the sender's email address
   # family = the list of all recipients' email addresses
   msg['From'] = '<Report Mailer> reportserver@pce.ca'
   msg['To'] = 'rmata@pce.ca'
   msg.preamble = 'You will not see this in a MIME-aware mail reader.\n'
   msg.set_content("""\
Please find report attached
""")

   # Open the files in binary mode.  You can also omit the subtype
   # if you want MIMEImage to guess it.
   if attachments:
      print('adding attachments')
      with open(attachments, 'rb') as content_file:
         content = content_file.read()
         msg.add_attachment(content, maintype='application', subtype='xls', filename='report.xlsx')

   # Send the email via our own SMTP server.
   with smtplib.SMTP('localhost') as s:
      s.send_message(msg)