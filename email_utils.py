import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


SENDER_EMAIL = "korupoludeekshit2021@gmail.com"
APP_PASSWORD = "EMAIL Password"


def send_grievance_email(
    student_name,
    student_email,
    ticket_no,
    department,
    status
):

    subject = "GITAM Grievance Registered"

    body = f"""
Dear {student_name},

Your grievance has been successfully registered.

Ticket Number:
{ticket_no}

Department:
{department}

Current Status:
{status}

You can use the ticket number to track your complaint.

Regards,
GITAM Grievance Portal
"""

    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = student_email
    msg["Subject"] = subject

    msg.attach(
        MIMEText(body, "plain")
    )

    try:

        server = smtplib.SMTP(
            "smtp.gmail.com",
            587
        )

        server.starttls()

        server.login(
            SENDER_EMAIL,
            APP_PASSWORD
        )

        server.send_message(msg)

        server.quit()

        return True

    except Exception as e:

        print(e)

        return False