import smtplib as smtp
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from objects import User


def send_email(email, code, forgot_password=False):
    sender_email = "swengtest20@gmail.com"
    receiver_email = email

    message = MIMEMultipart("alternative")
    message["Subject"] = (
        "[Traveller Blog] Reset Password"
        if forgot_password
        else "[Traveller Blog] Complete Registration"
    )
    message["From"] = sender_email
    message["To"] = receiver_email

    if forgot_password:
        text = """\
        Hello, {0} please use the following code to reset your password {1}\
        """.format(
            receiver_email, code
        )
    else:
        text = """\
        Hello, {0} welcome to our community, Blog Made Right
        Your code to complete registration : {1}\
        """.format(
            receiver_email, code
        )

    part1 = MIMEText(text, "plain")
    message.attach(part1)

    port = 465

    context = ssl.create_default_context()

    with smtp.SMTP_SSL(
        "smtp.gmail.com",
        port,
        context=context,
    ) as server:
        server.login(sender_email, "Catman123.")
        server.sendmail(sender_email, receiver_email, message.as_string())
