import os
import logging
import datetime
import json
import csv
from zoneinfo import ZoneInfo

from typing import Set, List, Union, Dict
from twilio.rest import Client as TwilioClient
import json

class SendUtils:
    def __init__(self):
        pass

    @staticmethod
    def single_message(client: TwilioClient, toNumber: str, fromNumber: str, body: str) -> bool:
        """Sends a single message from one number to another"""
        try:
            client.api.account.messages.create(to=toNumber, from_=fromNumber, body=body)
            return True
        except Exception as exception:
            logging.error(exception, exc_info=True)
            return False

    @staticmethod
    def get_current_datetime(override_datetime: datetime.datetime) -> datetime.datetime:
        """Returns localized datetime object if override datetime not present"""
        local_datetime: datetime.datetime = datetime.datetime.now(ZoneInfo("America/New York"))
        return local_datetime if not override_datetime else override_datetime 

    @staticmethod
    def get_current_roomie() -> str:
        """Determines current roomate"""
        with open('roomies_current.json') as roomies_current_file:
            current_roomie: str = json.load(roomies_current_file)["current"]
        return current_roomie

    @staticmethod
    def get_current_roomie_number() -> str:
        """Determines current roomate"""
        with open('roomies.json') as roomies_file:
            current_roomie_number: str = json.load(roomies_file)[SendUtils.get_current_roomie()]
        return current_roomie_number

    @staticmethod
    def get_next_roomie(override_datetime: datetime.datetime = None) -> str:
        """Determines the roomie next up in the order from the current roomate"""
        current_date: datetime.date = SendUtils.get_current_datetime(override_datetime).date()

        roomies_absences_list: List[List[str]]
        with open('roomies_absences.csv') as roomies_absences_file:
            roomies_absences_list = [row for idx, row in enumerate(csv.reader(roomies_absences_file, delimiter=',')) if idx > 0]

        abscence_row_format: List[List[Union(str, datetime.date)]]
        next_roomie_absences_list: List[List[Union(str, datetime.date)]]
        abscence_row_format = lambda row: [row[0], datetime.date.fromisoformat(row[1]), datetime.date.fromisoformat(row[2])]
        roomies_absences_list = [abscence_row_format(row) for row in roomies_absences_list]
        current_roomie: str = SendUtils.get_current_roomie()

        with open('roomies_order.json') as roomies_order_file:
            roomies_order: Dict[str, str] = json.load(roomies_order_file)

            while roomies_order[current_roomie] in [row[0] for row in roomies_absences_list]:
                next_roomie_absences_list = [row for row in roomies_absences_list if row[0] == roomies_order[current_roomie]]
                filtered_next_roomie_absences_list = list(filter(lambda row: row[1] < current_date < row[2], next_roomie_absences_list))
                if len(filtered_next_roomie_absences_list) > 0:
                    current_roomie = roomies_order[current_roomie]
                else:
                    break

            return roomies_order[current_roomie]

    @staticmethod
    def set_current_roomie(roomie: str) -> bool:
        """Writes the next current roomie to roomies_current.json"""
        try:
            with open('chores.json') as chores_file:
                chores: Dict[str, Dict[str,str]] = json.load(chores_file)

            roomies_current: Dict[str, str] = {time : "False" for time in chores.keys()}
            roomies_current.setdefault("current", roomie)

            with open('roomies_current.json', 'w') as roomies_current_file:
                json.dump(roomies_current, roomies_current_file)

            return True

        except Exception as exception:
            logging.error(exception, exc_info=True)
            return False

    @staticmethod
    def set_chore(hour: int, status: bool) -> bool:
       """Sets key/value pairs in the roomies current json file"""
        try:
            with open('roomies_current.json') as roomies_current_file:
                roomies_current: Dict["str", "str"] = json.load(roomies_current_file)
                roomies_current[str(hour)] = str(status)

            with open('roomies_current.json', 'w') as roomies_current_file:
                json.dump(roomies_current, roomies_current_file)

        except Exception as exception:
            logging.error(exception, exc_info=True)
            return False

    @staticmethod
    def get_is_message_due(override_datetime: datetime.datetime = None) -> bool:
        """Determines if a message is due to be sent"""
        current_datetime: datetime.datetime = SendUtils.get_current_datetime(override_datetime) 
        with open('chores.json') as chores_file:
            chores: Dict[str, Dict[str,str]] = json.load(chores_file)

        with open('roomies_current.json') as roomies_current_file:
            roomies_current: Dict["str", "str"] = json.load(roomies_current_file) 

        return (str(current_datetime.hour) in chores) and roomies_current[str(current_datetime.hour)] == 'False'

    @staticmethod
    def get_message(roomie: str, override_datetime: datetime.datetime = None) -> str:
        """Determines the message that is due on the current hour"""
        try:
            current_datetime: datetime.datetime = SendUtils.get_current_datetime(override_datetime)
            with open('chores.json') as chores_file:
                chores: Dict[str, Dict[str,str]] = json.load(chores_file)
            return chores[str(current_datetime.hour)]['body_fragment'].format(roomie=roomie)

        except Exception as exception:
            logging.error("Invaid message request at time {}".format(str(datetime.datetime.now())), exc_info=True)

    @staticmethod
    def cron_cycle_handle(client: TwilioClient, tyrant_number: str, override_datetime: datetime.datetime = None) -> bool:
        """Handles timing of chore messages and roomie switchovers"""
        try:
            current_datetime: datetime.datetime = SendUtils.get_current_datetime(override_datetime)

            if SendUtils.get_is_message_due(current_datetime):
                body: str = SendUtils.get_message(SendUtils.get_current_roomie())
                if SendUtils.single_message(client, SendUtils.get_current_roomie_number(), tyrant_number, body):
                    SendUtils.set_chore(SendUtils.get_current_roomie(), "True")
                logging.info("Cron cycle attempted a message send to {0} with body {1}".format(SendUtils.single_message, body))

            if current_datetime.hour == 23:
                last_roomie: str = SendUtils.get_current_roomie()
                SendUtils.set_current_roomie(SendUtils.get_next_roomie(override_datetime))
                logging.info("Cron cycle changed current roomie from {0} to {1}".format(last_roomie, SendUtils.get_current_roomie()))

            else:
                logging.info("Cron cycle did not carry out any actions")

        except Exception as exception:
            logging.error("Cron cycle error: {}".format(str(datetime.datetime.now())), exc_info=True)
            return False

        return True
