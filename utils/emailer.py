import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os

def send_email(receiver_email, subject, body, file_path, sender_email, sender_password):
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject

    # Attach file
    with open(file_path, "rb") as f:
        mime = MIMEBase("application", "octet-stream")
        mime.set_payload(f.read())
        encoders.encode_base64(mime)
        mime.add_header("Content-Disposition", f"attachment; filename={os.path.basename(file_path)}")
        msg.attach(mime)

    # Send via Gmail SMTP
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)