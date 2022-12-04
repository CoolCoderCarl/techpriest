import logging
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict

import pytz as pytz
import requests
from telethon import TelegramClient

import mongodb

API_ID = os.environ["API_ID"]
API_HASH = os.environ["API_HASH"]
SESSION = os.environ["SESSION"]

CLIENT = TelegramClient(SESSION, API_ID, API_HASH)

# Telegram configuration
BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

# Search configuration
try:
    SEARCH_PLACES_LIST = Path("search_places.txt")
    logging.info(f"File {SEARCH_PLACES_LIST.name} load successfully !")
except FileNotFoundError as file_not_found:
    logging.error(file_not_found)
    exit(1)

SEARCH_DEPTH_DAYS = 60


# Logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.WARNING
)
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.ERROR
)

cranial_scheme = mongodb.MongoDB()


def load_search_places_file():
    try:
        with open(SEARCH_PLACES_LIST, mode="r") as s_p_l:
            result = [place for place in s_p_l.read().split()]
            logging.info("File load successfully !")
            return result
    except FileNotFoundError as file_not_found:
        logging.error(file_not_found)
        exit(1)


def send_message_to_telegram(message: Dict, chat_id: str):
    """
    Send messages from telegram to telegram
    :param message:
    :param chat_id:
    :return:
    """
    try:
        response = requests.post(
            API_URL,
            json={
                "chat_id": chat_id,
                "text": f"{message['TEXT']}\n"
                "\n"
                f"{message['DATE']}\n"
                "\n"
                f"{message['MSG_URL']}",
            },
        )
        if response.status_code == 200:
            logging.info(
                f"Sent: {response.reason}. Status code: {response.status_code}"
            )
        else:
            logging.error(
                f"Not sent: {response.reason}. Status code: {response.status_code}"
            )
            logging.error(f"Detailed response: {response.text}")
    except Exception as err:
        logging.error(err)


def search_depth_days() -> datetime:
    today = datetime.now().replace(tzinfo=pytz.UTC)
    result = today - timedelta(days=SEARCH_DEPTH_DAYS)
    logging.info(f"Diapason is from {today} to {result}.")
    return result


def search(search_places: str, search_query: str) -> Dict:
    s_d_d = search_depth_days()
    time.sleep(60)
    for message in CLIENT.iter_messages(
        search_places, search=search_query, reverse=True
    ):
        logging.info(f"MESSAGE MEDIA: {message.media}")
        if message.date > s_d_d:
            if cranial_scheme.is_message_id_exist(
                message.peer_id.channel_id, message.id
            ):
                logging.warning(
                    f"Message with ID {message.id} already exist in db from channel {message.peer_id.channel_id}."
                )
                time.sleep(2)
            else:
                cranial_scheme.insert_data_to_db(
                    data_to_insert={str(message.peer_id.channel_id): str(message.id)},
                    database_name=cranial_scheme.MESSAGES_IDS_DB,
                    collection=cranial_scheme.messagesids_collection,
                )
                yield {
                    "TEXT": message.text,
                    "DATE": message.date,
                    "MSG_URL": f"https://t.me/c/{message.peer_id.channel_id}/{message.id}",
                }
        else:
            logging.warning(
                f"Wrong date diapason {message.date} < {s_d_d} | Skipping..."
            )


def main():
    while True:
        for places_to_search in load_search_places_file():
            for chat_id, search_query in cranial_scheme.get_data_from_db(
                "searchdb"
            ).items():
                logging.info(
                    f"Searching in {places_to_search} | for {search_query} | send to {chat_id}"
                )
                time.sleep(60)
                for message in search(places_to_search, search_query):
                    send_message_to_telegram(message, chat_id)
                    # print('Send to telegram')
                    time.sleep(60)
                else:
                    logging.info(
                        f"All founded messages about {search_query} in {places_to_search} were sent to {chat_id} !"
                    )
                    logging.info("Take a break for 5 min.")
                    time.sleep(300)


if __name__ == "__main__":
    CLIENT.start()
    main()
    # CLIENT.run_until_disconnected()
    # CLIENT.loop.run_until_complete(main())
