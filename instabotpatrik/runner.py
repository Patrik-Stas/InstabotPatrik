#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import pymongo
import instabotpatrik
import logging


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
        self.api_client = api_client if api_client is not None \
            else instabotpatrik.client.InstagramClient(user_login=self.cfg.get_instagram_username(),
                                                       user_password=self.cfg.get_instagram_password(),
                                                       requests_session=requests.Session(),
                                                       try_to_load_session_from_file=True)

        # INSTABOT DEPENDENCIES
        self.core = instabotpatrik.core.UserController(repository=self.repo_bot,
                                                       api_client=self.api_client)

        self.strategy_tag_selection = instabotpatrik.strategy.StrategyTagSelectionBasic(self.repo_config.get_tags)

        # CONTROLLERS
        self.account_controller = instabotpatrik.core.AccountController(self.repo_bot, self.api_client)
        self.user_controller = instabotpatrik.core.UserController(self.repo_bot, self.api_client)
        self.media_controller = instabotpatrik.core.MediaController(self.repo_bot, self.api_client)

        # INSTABOT
        self.instabot = instabotpatrik.instabot.InstaBot(login_controller=self.account_controller,
                                                         user_controller=self.user_controller,
                                                         media_controller=self.media_controller,
                                                         strategy_tag_selection=self.strategy_tag_selection)

    def run(self):
        self.instabot.run()

    def stop(self):
        self.instabot.stop()
