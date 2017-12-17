#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import pymongo
import instabotpatrik
import logging

logging.getLogger().setLevel(20)
logging.basicConfig(format='[%(levelname)s] [%(asctime)s] %(message)s', datefmt='%m/%d/%Y-%H:%M:%S')


class BasicSetup:
    def __init__(self, cfg, api_client=None):
        # CONFIGURATION
        self.cfg = cfg

        # DATABASE
        self.mongo_client = pymongo.MongoClient(self.cfg.get_db_host(), self.cfg.get_db_port())
        self.repo_bot = \
            instabotpatrik.repository.BotRepositoryMongoDb(mongo_client=self.mongo_client,
                                                           database_name=self.cfg.get_db_name(),
                                                           users_collection_name=self.cfg.collection_users_name(),
                                                           media_collection_name=self.cfg.collection_media_name())

        self.repo_config = \
            instabotpatrik.repository.ConfigRepositoryMongoDb(database_name=self.cfg.get_db_name(),
                                                              config_collection_name=self.cfg.collection_config_name(),
                                                              mongo_client=self.mongo_client)

        # API CLIENT
        self.client = api_client if api_client is not None \
            else instabotpatrik.client.InstagramClient(user_login=self.cfg.get_instagram_username(),
                                                       user_password=self.cfg.get_instagram_password(),
                                                       requests_session=requests.Session())

        # INSTABOT DEPENDENCIES
        self.core = instabotpatrik.core.InstabotCore(repository=self.repo_bot,
                                                     api_client=self.client)

        self.strategy_media_scan = instabotpatrik.strategy.StrategyMediaScanBasic(core=self.core)
        self.strategy_tag_selection = instabotpatrik.strategy.StrategyTagSelectionBasic(self.repo_config.get_tags)

        # INSTABOT
        self.instabot = instabotpatrik.instabot.InstaBot(core=self.core,
                                                         strategy_tag_selection=self.strategy_tag_selection,
                                                         strategy_media_scan=self.strategy_media_scan)

    def run(self):
        self.instabot.run()

    def stop(self):
        self.instabot.stop()
