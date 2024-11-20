import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os

def send_email(recipient_email, filename, first_name):
    # Email configuration (replace with your email settings)
    sender_email = "astrologiaclaracruz@gmail.com"  # Your email
    sender_password = "tbci ltuv llgv fqbw"  # Use an app password for security
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    # Create the email message
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = recipient_email
    message['Subject'] = f"Birth Chart for {first_name}"

    # Email body
    body = f"Dear {first_name},\n\nPlease find attached your birth chart planetary positions."
    message.attach(MIMEText(body, 'plain'))

    # Attach the file
    with open(filename, 'rb') as file:
        part = MIMEApplication(file.read(), Name=os.path.basename(filename))
        part['Content-Disposition'] = f'attachment; filename="{os.path.basename(filename)}"'
        message.attach(part)

    # Send the email
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(message)
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False