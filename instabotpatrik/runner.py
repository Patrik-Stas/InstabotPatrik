#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import pymongo
import instabotpatrik


class BasicSetup:
    def __init__(self, cfg):
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
            instabotpatrik.repository.ConfigRepositoryMongoDb(database_name=self.mongo_client,
                                                              config_collection_name=self.cfg.collection_config_name(),
                                                              mongo_client=self.mongo_client)

        # API CLIENT
        self.client = instabotpatrik.client.InstagramClient(user_login=self.repo_config.get_username(),
                                                            user_password=self.repo_config.get_password(),
                                                            requests_session=requests.Session())

        # INSTABOT DEPENDENCIES
        self.core = instabotpatrik.core.InstabotCore(repository=self.repo_bot,
                                                     api_client=self.client)
        self.strategy_like = instabotpatrik.strategy.StrategyLikeBasic(core=self.core)
        self.strategy_follow = instabotpatrik.strategy.StrategyFollowBasic(core=self.core)
        self.strategy_media_scan = instabotpatrik.strategy.StrategyMediaScanBasic(core=self.core)
        self.strategy_tag_selection = instabotpatrik.strategy.StrategyTagSelectionBasic(self.repo_config.get_tags)
        self.strategy_unfollow = instabotpatrik.strategy.StrategyUnfollowBasic(core=self.core)

        # INSTABOT
        self.instabot = instabotpatrik.instabot.InstaBot(core=self.core,
                                                         instagram_client=self.client,
                                                         repository_bot=self.repo_bot,
                                                         repository_config=self.repo_config,
                                                         strategy_tag_selection=self.strategy_tag_selection,
                                                         strategy_media_scan=self.strategy_media_scan,
                                                         strategy_like=self.strategy_like,
                                                         strategy_follow=self.strategy_follow,
                                                         strategy_unfollow=self.strategy_unfollow)

    def run(self):
        self.instabot.run()

    def stop(self):
        self.instabot.stop()
