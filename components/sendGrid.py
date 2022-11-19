import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase


def alert(main_msg):
   msg = MIMEMultipart()
   msg['From'] = mail_from
   msg['To'] = mail_to
   msg['Subject'] = '!Alert Mail On Product Shortage! - Regards'
   mail_body = main_msg
   msg.attach(MIMEText(mail_body))

   try:
      server = smtplib.SMTP_SSL('smtp.sendgrid.net', 465)
      server.ehlo()
      server.login('apikey', 'SG.ngeJheYFYQlKU0ufo8x5d1A.TwL2iGABfnBvoTf-09kqeF8tAmbihYzrnopKc-1s5cr')
      server.sendmail('ucs19430@rmd.ac.in', 'siva@gmail.com')
      server.close()
      print("mail sent")
   except:
      print("issue")