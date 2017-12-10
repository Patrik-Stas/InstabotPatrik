# -*- coding: utf-8 -*-
from testse2e.context import instabotpatrik
from testse2e import common
import unittest
import pymongo
import yaml
import os
import time
import logging


class ItShouldLoginAndGetMedia(unittest.TestCase):
    @staticmethod
    def get_path_to_file_in_directory_of_this_file(file_name):
        this_directory_absolute = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        return os.path.join(this_directory_absolute, file_name)

    def load_instagram_credentials(self):
        with open(self.get_path_to_file_in_directory_of_this_file("credentials.secret.yaml"), 'r') as stream:
            try:
                return yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)

    def setUp(self):
        print("Assure DB doesn't exists on start")
        self.config = common.get_config()
        self.mongo_client = pymongo.MongoClient(self.cfg.get_db_host(), self.cfg.get_db_port())
        bot_runner = instabotpatrik.runner.BasicSetup(self.config)
        bot_runner.run()

    def tearDown(self):
        logging.info("E2E tearDown DB cleanup. Dropping database %s", self.config.get_db_name())
        self.mongo_client.drop_database(self.config.get_db_name())

    def runTest(self):
        bot_runner = instabotpatrik.runner.BasicSetup(cfg=self.config)
        bot_runner.run()
        time.sleep(60)
        bot_runner.stop()
