import smtplib, ssl
from flask import current_app
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send(sender_email, receiver_email, subject, html_message, plain_text_message):
    """Sends an email from the sender emal to the receiver email.

    Arguments:
        sender_email {string} -- Email that is sending this message
        receiver_email {string} -- Email that is receiving the message
        subject {string} -- Subject of the message
        html_message {string} -- Message formatted in a HTML format
        plain_text_message {string} -- Message formatter in plain text
    """

    context = ssl.create_default_context()
    with smtplib.SMTP(current_app.config["SMTP_HOST"], current_app.config["SMTP_PORT"]) as server:

        # Note that the connection is not secured but the paylods being exchanged
        # is being encrypted

        # Key exchange for payload encryption
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()

        # Login
        server.login(current_app.config["SMTP_LOGIN"], current_app.config["SMTP_PASSWORD"])

        # Construct messsage
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = sender_email
        message["To"] = receiver_email

        plain_part = MIMEText(plain_text_message, "text")
        html_part = MIMEText(html_message, "html")

        message.attach(plain_part)
        message.attach(html_part)

        server.sendmail(sender_email, receiver_email, message.as_string())
