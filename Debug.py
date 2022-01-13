from datetime import date, datetime
import os
import logging
import datetime
import time

import pytz
from dotenv import load_dotenv
from twilio.rest import Client as TwilioClient
from SendUtils import SendUtils

class Debug:
    def __init__(self):
        pass

    @staticmethod
    def main() -> None:
        os.chdir('/bots/textbot')
        load_dotenv()
        client: TwilioClient = TwilioClient(os.getenv("account_sid"), os.getenv("auth_token"))
        body = "Sent from the bot"
        SendUtils.single_message(client, "+15555555555", os.getenv("tyrant_number"), body)

Debug.main()
