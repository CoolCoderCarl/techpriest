import logging
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict

import pytz as pytz
import requests
from telethon import TelegramClient

import dynaconfig
import mongodb

# Session configuration
API_ID = os.environ["API_ID"]
API_HASH = os.environ["API_HASH"]
SESSION = os.environ["SESSION"]

CLIENT = TelegramClient(SESSION, API_ID, API_HASH)

# Telegram configuration
BOT_TOKEN = dynaconfig.settings["TELEGRAM"]["BOT_TOKEN"]
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

# Search configuration
SEARCH_PLACES_LIST = Path("search_places.txt")
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
            logging.info(f"Detailed response: {response.text}")
        else:
            logging.error(
                f"Not sent: {response.reason}. Status code: {response.status_code}"
            )
            logging.error(f"Detailed response: {response.text}")
    except Exception as err:
        logging.error(err)


def search(search_places: str, search_query: str) -> Dict:
    for message in CLIENT.iter_messages(search_places, search=search_query):
        logging.info(f"MESSAGE MEDIA: {message.media}")
        yield {
            "TEXT": message.text,
            "DATE": message.date,
            "MSG_URL": f"https://t.me/c/{message.peer_id.channel_id}/{message.id}",
        }


def main():
    while True:
        today = datetime.now().replace(tzinfo=pytz.UTC)
        search_depth_days = today - timedelta(days=SEARCH_DEPTH_DAYS)
        logging.info(f"Sending from {today} to {search_depth_days} to the past.")
        for places_to_search in load_search_places_file():
            for chat_id, search_query in cranial_scheme.get_data_from_db().items():
                logging.info(
                    f"Searching in {places_to_search} | for {search_query} | send to {chat_id}"
                )
                for message in search(places_to_search, search_query):
                    if message["DATE"] > search_depth_days:
                        send_message_to_telegram(message, chat_id)
                        time.sleep(5)
                    else:
                        logging.warning(
                            "Out of diapason of date ! Take a break for 5 min."
                        )
                        time.sleep(300)
                else:
                    logging.warning(
                        "All founded messages were sent ! Take a break for 5 min."
                    )
                    time.sleep(300)


if __name__ == "__main__":
    CLIENT.start()
    main()
    # CLIENT.run_until_disconnected()
    # client.loop.run_until_complete(main())
