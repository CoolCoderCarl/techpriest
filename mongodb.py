import logging
import os
from pathlib import Path
from typing import Dict

import pymongo

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


class MongoDB:
    MONGO_URL = "mongodb://localhost:27017/"  # os.environ["MONGO_URL"]

    # TODO Check is file exists
    SEARCH_SCHEME_FILE = Path("search_scheme.txt")
    SEARCH_DB_NAME = "saerchdb"
    SEARCH_DB_TABLE = "chats_topics"

    mongo_client = pymongo.MongoClient(MONGO_URL)

    searchdb = mongo_client[SEARCH_DB_NAME]

    search_collection = searchdb[SEARCH_DB_TABLE]

    def __init__(self):
        # def purge_db_at_start(self):
        self.mongo_client.drop_database(self.SEARCH_DB_NAME)
        logging.warning("Database was purged at start !")

    # TODO Add validation func to check is data correct

    def __load_data_from_file(self, search_scheme: str) -> Dict:
        try:
            with open(search_scheme, mode="r") as f:
                d = dict(x.rstrip().split() for x in f)
                logging.info("Data was loaded from file to db successfully !")
                return d
        except FileExistsError as file_exist_err:
            logging.error(file_exist_err)
            return {}
        except BaseException as base_exception:
            logging.error(base_exception)
            return {}

    def insert_data_to_db(self):
        try:
            self.search_collection.insert_one(
                self.__load_data_from_file(self.SEARCH_SCHEME_FILE)
            )
            logging.info("Data was inserted successfully !")
        except BaseException as base_exception:
            logging.error("Data was not inserted successfully !")
            logging.error(base_exception)
            raise Exception

    def is_db_exist(self) -> bool:
        if self.searchdb.name in self.mongo_client.list_database_names():
            logging.info(f"Database {self.searchdb} already exists")
            return True
        else:
            logging.warning(f"Database {self.searchdb} do not exists !")
            return False

    def get_data_from_db(self):
        for db in self.search_collection.find():
            print(db)
            print(type(db))


if __name__ == "__main__":
    cranial_scheme = MongoDB()
    if cranial_scheme.is_db_exist():
        cranial_scheme.get_data_from_db()
    else:
        cranial_scheme.insert_data_to_db()
