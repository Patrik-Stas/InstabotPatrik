#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import pymongo

from instabotpatrik.core import InstabotCore
from instabotpatrik.repository import BotRepositoryMongoDb
from instabotpatrik.repository import ConfigRepositoryMongoDb
from instabotpatrik.instabot import InstaBot
from instabotpatrik.client import InstagramClient
from instabotpatrik.strategy import StrategyLikeBasic
from instabotpatrik.strategy import StrategyFollowBasic
from instabotpatrik.strategy import StrategyMediaScanBasic
from instabotpatrik.strategy import StrategyTagSelectionBasic
from instabotpatrik.strategy import StrategyUnfollowBasic

# sys.path.append(os.path.join(sys.path[0], 'instabotpatrik'))

mongo_client = pymongo.MongoClient('localhost', 27017)
repo_bot = BotRepositoryMongoDb(mongo_client)
repo_config = ConfigRepositoryMongoDb(mongo_client)
client = InstagramClient(user_login=repo_config.get_username(),
                         user_password=repo_config.get_password(),
                         requests_session=requests.Session())
core = InstabotCore(repository=repo_bot,
                    api_client=client)
strategy_like = StrategyLikeBasic(core=core)
strategy_follow = StrategyFollowBasic(core=core)
strategy_media_scan = StrategyMediaScanBasic(core=core)
strategy_tag_selection = StrategyTagSelectionBasic(repo_config.get_tags)
strategy_unfollow = StrategyUnfollowBasic(core=core)

InstaBot(core=core,
         instagram_client=client,
         repository_bot=repo_bot,
         repository_config=repo_config,
         strategy_tag_selection=strategy_tag_selection,
         strategy_media_scan=strategy_media_scan,
         strategy_like=strategy_like,
         strategy_follow=strategy_follow,
         strategy_unfollow=strategy_unfollow)