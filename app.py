from flask import Flask, request
from tasks import send_email_task
import datetime
import re


app = Flask(__name__)

def is_email_valid(email):
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(regex, email)

@app.route('/')
def index():
    sendmail = request.args.get('sendmail')
    talktome = request.args.get('talktome')

    if sendmail:
        if not is_email_valid(sendmail):
            return "Invalid email address.", 400

        send_email_task.delay(sendmail)
        return f"Email to {sendmail} is being sent."

    if talktome:
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("/var/log/messaging_system.log", "a") as log_file:
            log_file.write(f"{current_time}\n")
        return "Current time logged."

    return "Welcome to the messaging system!"


@app.route('/logs')
def get_logs():
    try:
        with open('/var/log/messaging_system.log', 'r') as f:
            logs = f.read()
        return logs, 200, {'Content-Type': 'text/plain; charset=utf-8'}
    except Exception as e:
        return f"Failed to retrieve logs: {str(e)}", 500


if __name__ == '__main__':
    app.run(debug=True)

