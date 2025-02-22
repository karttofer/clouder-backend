import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_API_KEY = os.getenv("SENDER_API_KEY")

# Your email credentials
sender_email = SENDER_EMAIL
sender_password = SENDER_API_KEY


# Recipient email address
def send_email(recipient_email, subject, body):
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    smtp_server = "smtp-relay.brevo.com"
    smtp_port = 587

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()

    server.login(sender_email, sender_password)

    server.sendmail(sender_email, recipient_email, message.as_string())

    server.quit()
    print("Email sent successfully!")
