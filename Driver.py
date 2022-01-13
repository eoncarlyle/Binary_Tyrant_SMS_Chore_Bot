from datetime import datetime
import os
import logging

import pytz
from dotenv import load_dotenv
from twilio.rest import Client as TwilioClient
from SendUtils import SendUtils

class Driver:
    def __init__(self):
        pass

    @staticmethod
    def main() -> None:
        os.chdir('/bots/textbot')
        load_dotenv()
        logging.basicConfig(filename='sms.log', format='%(asctime)s:%(message)s', level=logging.INFO)
        logging.info("Invocation of main in Driver.py")
        client: TwilioClient = TwilioClient(os.getenv("account_sid"), os.getenv("auth_token"))
        SendUtils.cron_cycle_handle(client, os.getenv("tyrant_number"))

Driver.main()
