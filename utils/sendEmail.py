import smtplib
import getpass

HOST = 'smtp-mail.outlook.com'
PORT = 587

def is_smtp_connection_valid(smtp):
    try:
        status = smtp.noop()
        if status[0] == 250:
            return True
        else:
            return False
    except smtplib.SMTPServerDisconnected:
        return False
    except smtplib.SMTPException as e:
        print(f"SMTP exception occurred: {e}")
        return False

def connect_to_smtp():
    try:
        smtp = smtplib.SMTP(HOST, PORT)
        status_code, response = smtp.ehlo()
        print(f"Echoing the server: {status_code} {response}")

        smtp.starttls()
        smtp.login('bseupdater@outlook.com', password)
        print("Login Successful")
        return smtp
    except smtplib.SMTPException as e:
        print(f"Error occurred during connection: {e}")
        return None

def send_email(message: str):
    global smtp
    if not is_smtp_connection_valid(smtp):
        print("SMTP connection is no longer valid. Reconnecting...")
        smtp.quit()
        smtp = connect_to_smtp()
        if smtp is None:
            print("Reconnection failed. Unable to send email.")
            return
    try:
        smtp.sendmail('bseupdater@outlook.com', 'anmol03kw@gmail.com', message)
        print('Mail sent')
    except smtplib.SMTPException as e:
        print(f"Failed to send email: {e}")
    finally:
        smtp.quit()


password = getpass.getpass("Password: ")
smtp = connect_to_smtp()

# try:
#     password = getpass.getpass("Password: ")
#     smtp = connect_to_smtp()
#     if smtp is not None:
#         send_email("Your email message here")
#     else:
#         print("Initial connection failed. Exiting.")
# except smtplib.SMTPException as e:
#     print(f"Error occurred: {e}")
