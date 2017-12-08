#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import pymongo
import argparse
import instabotpatrik

parser = argparse.ArgumentParser(description='Instagram follow/unfollow/like automation')
argparse.parser.add_argument('--config-file',
                             default="dev.ini",
                             help='Path to configuration file')
args = vars(parser.parse_args())

config = instabotpatrik.config.Config(config_path=args['config-file'])

mongo_client = pymongo.MongoClient('localhost', 27017)
repo_bot = instabotpatrik.repository.BotRepositoryMongoDb(mongo_client=mongo_client,
                                                          database_name=config.get_db_name(),
                                                          users_collection_name=config.get_collection_users_name(),
                                                          media_collection_name=config.get_collection_media_name())

repo_config = instabotpatrik.repository.ConfigRepositoryMongoDb(mongo_client)
client = instabotpatrik.client.InstagramClient(user_login=repo_config.get_username(),
                                               user_password=repo_config.get_password(),
                                               requests_session=requests.Session())
core = instabotpatrik.core.InstabotCore(repository=repo_bot,
                                        api_client=client)
strategy_like = instabotpatrik.strategy.StrategyLikeBasic(core=core)
strategy_follow = instabotpatrik.strategy.StrategyFollowBasic(core=core)
strategy_media_scan = instabotpatrik.strategy.StrategyMediaScanBasic(core=core)
strategy_tag_selection = instabotpatrik.strategy.StrategyTagSelectionBasic(repo_config.get_tags)
strategy_unfollow = instabotpatrik.strategy.StrategyUnfollowBasic(core=core)

instabotpatrik.instabot.InstaBot(core=core,
                                 instagram_client=client,
                                 repository_bot=repo_bot,
                                 repository_config=repo_config,
                                 strategy_tag_selection=strategy_tag_selection,
                                 strategy_media_scan=strategy_media_scan,
                                 strategy_like=strategy_like,
                                 strategy_follow=strategy_follow,
                                 strategy_unfollow=strategy_unfollow)
