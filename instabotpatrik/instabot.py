#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import time
import logging
import instabotpatrik

class InstaBot:

    def __init__(self,
                 instagram_client,
                 repository_bot,
                 repository_config,
                 strategy_tag_selection,
                 strategy_media_scan,
                 strategy_like,
                 strategy_follow,
                 strategy_unfollow):

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

    def is_action_allowed_now(self, action_name):
        return time.time() > self.actions_timestamps[action_name]

    def allow_action_after(self, action_name, allowed_after_timestamp):
        self.actions_timestamps[action_name] = allowed_after_timestamp

    def can_like(self):
        return self.like_per_day > 0 and self.is_action_allowed_now("like")

    def can_follow(self):
        return self.follow_per_day > 0 and self.is_action_allowed_now("follow")

    def can_unfollow(self):
        return self.unfollow_per_day > 0 and self.is_action_allowed_now("unfollow")

    def run(self):
        if not self.instagram_client.is_logged_in():
            logging.error("Bot can't run because Instagram client is not logged in.")
            return

        while True:
            try:
                tag = self.strategy_tag_selection.get_tag()
                media = self.strategy_media_scan.get_latest_media_by_tag(tag)

                logging.info("Media iteration for tag:%s", tag)

                if self.can_like():
                    self.strategy_like.like(media)
                if self.can_follow():
                    self.strategy_follow.follow(media)
                if self.can_unfollow():
                    followed_users = self.repository_bot.find_followed_user()
                    self.strategy_unfollow.unfollow(followed_users)

                instabotpatrik.tools.go_sleep(duration_sec=3, plusminus=2)
            except Exception as e:
                logging.error(e, exc_info=True)
                instabotpatrik.tools.go_sleep(duration_sec=100, plusminus=15)
