from twilio.rest import Client
import os
import httpx
from dotenv import load_dotenv
load_dotenv()

os.environ['AUTH_TOKEN'] = os.getenv('Twilio_auth_token')
os.environ['ACCOUNT_SID'] = os.getenv('Twilio_acc_SID')

def sendSMSNotification(numbers : list[str], message : str):
    client = Client(os.environ['ACCOUNT_SID'], os.environ['AUTH_TOKEN'])
    for number in numbers: 
        sms = client.messages.create(
            body=message, 
            to=number, 
            messaging_service_sid='MGb955970f378a8cda7b2aaaf02f87ec19'
        )
        print("Message sent successfully")
    return 





