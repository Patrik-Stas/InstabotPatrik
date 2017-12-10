#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import time
import logging
import instabotpatrik


class InstaBot:

    def __init__(self,
                 core,
                 instagram_client,
                 repository_bot,
                 repository_config,
                 strategy_tag_selection,
                 strategy_media_scan,
                 strategy_like,
                 strategy_follow,
                 strategy_unfollow):
        """
        :param core:
        :type core: instabotpatrik.core.InstabotCore
        :param instagram_client:
        :type instagram_client: instabotpatrik.client.InstagramClient
        :param repository_bot:
        :type repository_bot: instabotpatrik.repository.BotRepositoryMongoDb
        :param repository_config:
        :type repository_config: instabotpatrik.strategy.ConfigRepositoryMongoDb
        :param strategy_tag_selection:
        :type strategy_tag_selection: instabotpatrik.strategy.StrategyTagSelectionBasic
        :param strategy_media_scan:
        :type strategy_media_scan: instabotpatrik.strategy.StrategyMediaScanBasic
        :param strategy_like:
        :type strategy_like: instabotpatrik.strategy.StrategyLikeBasic
        :param strategy_follow:
        :type strategy_follow: instabotpatrik.strategy.StrategyFollowBasic
        :param strategy_unfollow:
        :type strategy_unfollow: instabotpatrik.strategy.StrategyUnfollowBasic
        """
        self.core = core
        self.bot_start = datetime.datetime.now()
        self.instagram_client = instagram_client
        self.strategy_tag_selection = strategy_tag_selection
        self.strategy_media_scan = strategy_media_scan
        self.strategy_like = strategy_like
        self.strategy_follow = strategy_follow
        self.strategy_unfollow = strategy_unfollow
        self.repository_bot = repository_bot
        self.repository_config = repository_config

        self.like_per_day = 300
        self.follow_per_day = 300
        self.unfollow_per_day = 200

        self.time_in_day = 24 * 60 * 60
        self.like_delay = self.time_in_day / self.like_per_day
        self.unfollow_delay = self.time_in_day / self.unfollow_per_day
        self.follow_delay = self.time_in_day / self.follow_per_day
        self.actions_timestamps = {}
        self.instagram_client.login()
        self.base_loop_timeout = 60 * 5
        self.tag_loop_timeout = 15
        self.error_timeout = 100
        self.stopped = False

    def is_action_allowed_now(self, action_name):
        return time.time() > self.actions_timestamps[action_name]

    def allow_action_after(self, action_name, allowed_after_timestamp):
        self.actions_timestamps[action_name] = allowed_after_timestamp

    def _can_like(self):
        return self.like_per_day > 0 and self.is_action_allowed_now("like")

    def _can_follow(self):
        return self.follow_per_day > 0 and self.is_action_allowed_now("follow")

    def _can_unfollow(self):
        return self.unfollow_per_day > 0 and self.is_action_allowed_now("unfollow")

    def time_left_till_allowed(self, action_name):
        self.actions_timestamps[action_name] - instabotpatrik.tools.get_time()

    def run(self):
        logging.info("Starting bot")
        if not self.instagram_client.is_logged_in():
            self.instagram_client.login()

        while not self.stopped:
            try:
                tag = self.strategy_tag_selection.get_tag()
                logging.info("Starting main loop. Selected tag: %s", tag)

                medias = self.strategy_media_scan.get_media(tag)
                logging.info("For tag %s received recent media %s", tag, "%s" % [media for media in medias])

                media_users = [self.core.get_media_owner(media) for media in medias]

                for loop in range(0, len(medias)):
                    if self._can_like():
                        self.strategy_like.like(medias)
                    if self._can_follow():
                        self.strategy_follow.follow(media_users)
                    if self._can_unfollow():
                        followed_users = self.repository_bot.find_followed_users()
                        self.strategy_unfollow.unfollow(followed_users)

                    instabotpatrik.tools.go_sleep(duration_sec=3, plusminus=2)
            except Exception as e:
                logging.error(e, exc_info=True)
                instabotpatrik.tools.go_sleep(duration_sec=100, plusminus=15)
        logging.info("Bot is stopped.")

    def stop(self):
        self.stopped = True
        logging.info("Stopped flag was set.")
