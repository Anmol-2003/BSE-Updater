import smtplib
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login('bhardwaj11kw@gmail.com', '#Kuwait04')

print("Login Successful")

def sendEmail(message : str):
    server.sendmail('from_email@gmail.com', 'to_email@gamil.com', message)
    return 