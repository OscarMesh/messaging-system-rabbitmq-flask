import os
from celery import Celery
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
import traceback

app = Celery('tasks', broker='pyamqp://guest@localhost//')

log_dir = os.path.join(os.path.expanduser("~"), "messaging_system_logs")
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(filename=os.path.join(log_dir, 'messaging_system.log'),
                    level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

@app.task
def send_email_task(to_email):
    from_email = "mprexhairs@gmail.com"
    from_password = "pgrdputfvmmkkmem"
    smtp_server = "smtp.gmail.com"
    smtp_port = 465

    try:
        logging.info(f"Connecting to SMTP server: {smtp_server}:{smtp_port}")
        with smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=30) as server:
            logging.info("Logging in")
            server.login(from_email, from_password)

            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = to_email
            msg['Subject'] = "Awesome HNG!"

            text = "Congrats! Email sent successfully"
            html = """
            <!doctype html>
            <html>
            <head>
                <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
            </head>
            <body>
                <p>Congrats email sent</p>
            </body>
            </html>
            """

            part1 = MIMEText(text, 'plain')
            part2 = MIMEText(html, 'html')

            msg.attach(part1)
            msg.attach(part2)

            logging.info("Sending email")
            server.sendmail(from_email, to_email, msg.as_string())

        print(f"Email sent successfully to {to_email}")
        logging.info(f"Email sent successfully to {to_email}")

    except (smtplib.SMTPException, IOError) as e:
        error_message = f"Failed to send email to {to_email}. Error: {str(e)}\n{traceback.format_exc()}"
        print(error_message)
        logging.error(error_message)
        raise send_email_task.retry(exc=e, countdown=60)

    except Exception as e:
        error_message = f"Unexpected error when sending email to {to_email}. Error: {str(e)}\n{traceback.format_exc()}"
        print(error_message)
        logging.error(error_message)
        raise
