#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
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
        self.current_tag = None

        self.like_per_day = 900
        self.follow_per_day = 300
        self.unfollow_per_day = 200

        self.time_in_day = 24 * 60 * 60
        self.like_delay_sec = self.time_in_day / self.like_per_day
        self.unfollow_delay_sec = self.time_in_day / self.unfollow_per_day
        self.follow_delay_sec = self.time_in_day / self.follow_per_day
        self.instagram_client.login()
        self._stopped = False
        self.action_manager = instabotpatrik.tools.ActionManager()

    def _can_like(self):
        return self.like_per_day > 0 and self.is_action_allowed_now("like")

    def _can_follow(self):
        return self.follow_per_day > 0 and self.is_action_allowed_now("follow")

    def _can_unfollow(self):
        return self.unfollow_per_day > 0 and self.is_action_allowed_now("unfollow")

    def handle_media_like(self, media):
        if self._can_like() and self.strategy_like.should_like(media):
            if self.core.like(media):
                self.action_manager.allow_action_after_seconds('like', self.like_delay_sec)

    def handle_user_follow(self, user):
        if self._can_follow() and self.strategy_follow.should_follow(user):
            if self.core.follow(user):
                self.action_manager.allow_action_after_seconds('follow', self.follow_delay_sec)

    def try_unfollow_someone(self):
        if self._can_unfollow():
            followed_users = self.repository_bot.find_followed_users()
            for user in followed_users:
                if self.strategy_unfollow.should_unfollow(user):
                    if self.core.unfollow(user):
                        self.action_manager.allow_action_after_seconds('unfollow', self.unfollow_delay_sec)
                        break

    def handle_recent_media(self, medias):
        logging.info("[INSTABOT] Handling recent media for tag %s. Media count: %d", self.current_tag, len(medias))
        logging.info("[INSTABOT] Recent media shortcodes: %s", [media.shortcode for media in medias])
        for media in medias:
            self.handle_media_like(media)
            owner = self.core.get_media_owner(media)
            if owner is None:
                logging.warning("[INSTABOT] Couldn't get details about media owner.")
            elif owner.detail.we_follow is False:
                self.handle_user_follow(owner)

            if self._stopped:
                break
            self.wait_until_some_action_possible()

    def wait_until_some_action_possible(self):
        sleep_sec = self.action_manager.time_left_until_some_action_possible()
        instabotpatrik.tools.go_sleep(duration_sec=sleep_sec + 3, plusminus=3)

    def run(self):
        logging.info("Starting bot with following configuration:")

        logging.info("like_per_day:%d  -> like_delay: %d " % (self.like_per_day, self.like_delay_sec))
        logging.info("follow_per_day:%d  -> unfollow_delay: %d " % (self.follow_per_day, self.unfollow_delay_sec))
        logging.info("unfollow_per_day:%d  -> follow_delay: %d " % (self.unfollow_per_day, self.follow_delay_sec))

        if not self.instagram_client.is_logged_in():
            self.instagram_client.login()

        while not self._stopped:
            try:
                self.current_tag = self.strategy_tag_selection.get_tag()
                logging.info("[INSTABOT] Starting main loop. Selected tag: %s", self.current_tag)

                medias = self.strategy_media_scan.get_media_of_other_people(self.current_tag)
                self.handle_recent_media(medias)
                self.try_unfollow_someone()
                self.wait_until_some_action_possible()
            except Exception as e:
                logging.error(e, exc_info=True)
                instabotpatrik.tools.go_sleep(duration_sec=100, plusminus=15)
        logging.info("Bot is stopped.")

    def stop(self):
        self._stopped = True
        logging.info("Stopped flag was set.")
