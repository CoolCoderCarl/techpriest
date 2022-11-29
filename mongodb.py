import logging
from pathlib import Path
from typing import Dict

import pymongo

import dynaconfig

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
    # __MONGO_URL = "mongodb://localhost:27017/"  # Use for local test
    __MONGO_URL = "mongodb://search_mongodb:27017/"  # Use to build image

    try:
        __SEARCH_SCHEME_FILE = Path("search_scheme.txt")
        logging.info("File load successfully !")
    except FileNotFoundError as file_not_found:
        logging.error(file_not_found)
        exit(1)

    # Authorization to mongodb
    __USERNAME = dynaconfig.settings["MONGODB"]["USERNAME"]
    __PASSWORD = dynaconfig.settings["MONGODB"]["PASSWORD"]

    # DB content
    __SEARCH_DB_NAME = "searchdb"
    __SEARCH_DB_TABLE = "searchtable"

    # __mongo_client = pymongo.MongoClient(__MONGO_URL)  # Use for local test
    __mongo_client = pymongo.MongoClient(__MONGO_URL, username=__USERNAME, password=__PASSWORD) # Use to build image
    __searchdb = __mongo_client[__SEARCH_DB_NAME]
    __search_collection = __searchdb[__SEARCH_DB_TABLE]

    # TODO Add validation func to check is data correct

    def __load_data_from_file(self, search_scheme: str) -> Dict:
        try:
            with open(search_scheme, mode="r", encoding="UTF-8") as file:
                result = dict(x.rstrip().split() for x in file)
                logging.info("Data was loaded from file to db successfully !")
                return result
        except FileExistsError as file_exist_err:
            logging.error(file_exist_err)
            return {}
        except BaseException as base_exception:
            logging.error(base_exception)
            return {}

    def __insert_data_to_db(self):
        try:
            self.__search_collection.insert_one(
                self.__load_data_from_file(self.__SEARCH_SCHEME_FILE)
            )
            logging.info("Data was inserted successfully !")
        except BaseException as base_exception:
            logging.error("Data was not inserted successfully !")
            logging.error(base_exception)
            raise Exception

    def __init__(self):
        # def purge_db_at_start(self):
        self.__mongo_client.drop_database(self.__SEARCH_DB_NAME)
        logging.warning("Database was purged at start !")
        self.__insert_data_to_db()

    def is_db_exist(self) -> bool:
        if self.__searchdb.name in self.__mongo_client.list_database_names():
            logging.info(f"Database {self.__searchdb} already exists")
            return True
        else:
            logging.warning(f"Database {self.__searchdb} do not exists !")
            return False

    def get_data_from_db(self) -> Dict:
        for db in self.__search_collection.find():
            logging.warning(f"The object ID {db['_id']} going to delete.")
            del db["_id"]
            logging.warning("The ID was deleted !")
            return db


if __name__ == "__main__":
    cranial_scheme = MongoDB()
    # while True:
    if cranial_scheme.is_db_exist():
        logging.info(cranial_scheme.get_data_from_db())
    else:
        logging.info(cranial_scheme.get_data_from_db())
    pass
