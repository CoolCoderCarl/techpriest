import logging
import os
import time
from datetime import datetime, timedelta
from typing import Dict

import pytz as pytz
import requests
from telethon import TelegramClient

import dynaconfig

# Session configuration
API_ID = os.environ["API_ID"]
API_HASH = os.environ["API_HASH"]
SESSION = os.environ["SESSION"]

CLIENT = TelegramClient(SESSION, API_ID, API_HASH)

# Telegram configuration
BOT_TOKEN = dynaconfig.settings["TELEGRAM"]["BOT_TOKEN"]
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
CHAT_ID = dynaconfig.settings["TELEGRAM"]["CHAT_ID"]

# Search configuration
# TODO move this conf when uploaded from mongo will be ready
SEARCH_QUERY = dynaconfig.settings["SEARCH"]["QUERY"]
SEARCH_PLACES = dynaconfig.settings["SEARCH"]["SEARCH_PLACES"]

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


def send_message_to_telegram(message: Dict):
    """
    Send messages from telegram to telegram
    :param message:
    :return:
    """
    try:
        response = requests.post(
            API_URL,
            json={
                "chat_id": CHAT_ID,
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
    except Exception as err:
        logging.error(err)


def search() -> Dict:
    logging.info(f"Searching in {SEARCH_PLACES} for {SEARCH_QUERY}.")
    for message in CLIENT.iter_messages(SEARCH_PLACES, search=SEARCH_QUERY):
        logging.info(f"MESSAGE MEDIA: {message.media}")
        yield {
            "TEXT": message.text,
            "DATE": message.date,
            "MSG_URL": f"https://t.me/c/{message.peer_id.channel_id}/{message.id}",
        }


if __name__ == "__main__":
    CLIENT.start()
    while True:
        today = datetime.now().replace(tzinfo=pytz.UTC)
        back_half_year = today - timedelta(days=60)
        logging.info(f"Sending from {today} to {back_half_year} to the past.")
        for message in search():
            if message["DATE"] > back_half_year:
                send_message_to_telegram(message)
                time.sleep(5)
            else:
                logging.warning("Out of diapason of date ! Take a break for 5 min.")
                time.sleep(300)
        else:
            logging.warning("All founded messages were sent ! Take a break for 5 min.")
            time.sleep(300)
    # CLIENT.run_until_disconnected()
    ### client.loop.run_until_complete(main())
