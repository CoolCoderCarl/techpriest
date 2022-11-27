import logging
import os
import time
from typing import Dict

import requests
from telethon import TelegramClient

import dynaconfig

# Session configuration
API_ID = os.environ["API_ID"]
API_HASH = os.environ["API_HASH"]
SESSION = os.environ["SESSION"]

CLIENT = TelegramClient(SESSION, API_ID, API_HASH)

# Telegram configuration
API_TOKEN = os.environ["API_TOKEN"]
API_URL = f"https://api.telegram.org/bot{API_TOKEN}/sendMessage"
CHAT_ID = os.environ["CHAT_ID"]

# Search configuration
SEARCH_QUERY = dynaconfig.settings["SEARCH_QUERY"]
PLACES_TO_SEARCH = dynaconfig.settings["PLACES_TO_SEARCH"]

# Logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.ERROR
)


def send_message_to_telegram(message):
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
    for message in CLIENT.iter_messages(PLACES_TO_SEARCH, search=SEARCH_QUERY):
        logging.info(f"MESSAGE MEDIA: {message.media}")
        yield {
            "TEXT": message.text,
            "DATE": message.date,
            "MSG_URL": f"https://t.me/c/{message.peer_id.channel_id}/{message.id}",
        }


if __name__ == "__main__":
    CLIENT.start()
    for i in search():
        send_message_to_telegram(i)
        time.sleep(5)
    CLIENT.run_until_disconnected()
    ### client.loop.run_until_complete(main())
