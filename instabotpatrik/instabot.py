#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import logging
import instabotpatrik
import random
import logging
import logging.handlers


# TODO : Limit cap middle layer
# TODO: Extract fetching media out - all I need is interface: get me this many media. I don't need to care where are
# those media coming from for now
# TODO: Some generalized scheduler class maybe?

# comment: I ideally on instabot layer I would really just say what actions/workflows I wanna do and how often I wanna
# do them. Groovy DSL for that? Python DSL? (programmable bot, but also with UI ...aiguuuu, total killer)

# TODO: annotations for scheduling... anotate method with @allowAfter(action='like', sec=300) ... and if the like was
# succesfull, then this annotation will asure to setup action manager to allow like only after 300 seconds

# TODO: Shall we add follow timestamp to user if we find out we follow him, but missing out dt_follow? (Happens if user
# is followed by other means than by bot (by instagram account owner directly)


class InstaBot:

    def __init__(self,
                 media_controller,
                 user_controller,
                 login_controller,
                 strategy_tag_selection):
        """
        :param media_controller:
        :type media_controller: instabotpatrik.core.MediaController
        :param user_controller:
        :type user_controller: instabotpatrik.core.UserController
        :param login_controller:
        :type login_controller: instabotpatrik.core.AccountController
        """
        # loghandler = logging.handlers.TimedRotatingFileHandler(filename="logfile.log", when="midnight", utc=True)
        # formatter = logging.Formatter(fmt='[%(levelname)s] [%(asctime)s] [%(name)s:%(funcName)s] : %(message)s',
        #                   datefmt='%m/%d/%Y-%H:%M:%S')
        self.logger = logging.getLogger(self.__class__.__name__)

        self.media_controller = media_controller
        self.user_controller = user_controller
        self.login_controller = login_controller

        self.bot_start = datetime.datetime.now()
        self.strategy_tag_selection = strategy_tag_selection

        # self.follow_per_day_cap = 150
        self.unfollow_per_day_cap = 73
        self.lfs_per_day_cap = 87  # lfs = like-follow-session

        self.time_in_day = 24 * 60 * 60
        self.ban_sleep_time_sec = 10 * 60 * 60  # how long sleep if we get non 2xx response

        self.lfs_delay_sec = self.time_in_day / self.lfs_per_day_cap
        self.unfollow_delay_sec = self.time_in_day / self.unfollow_per_day_cap

        self.action_manager = instabotpatrik.tools.ActionManager()
        self.unfollow_workflow = instabotpatrik.workflow.UnfollowWorkflow(user_controller=self.user_controller)
        self.lfs_workflow = instabotpatrik.workflow.LfsWorkflow(user_controller=self.user_controller,
                                                                media_controller=self.media_controller)

        self.select_ratio = 0.55

        self.logger.info("Created instabot. Unfollows per day:%d, LFS per day:%d.", self.unfollow_delay_sec,
                         self.lfs_per_day_cap)
        self.logger.info("Unfollow interval sec:%d, LFS interval sec:%d. ", self.unfollow_delay_sec,
                         self.lfs_delay_sec)
        self.logger.info("Sleep on non 2xx response: %d sec.", self.ban_sleep_time_sec)
        self.logger.info("Ratio of randomly selected media batch for tag: %f.", self.select_ratio)

        self.current_tag = None
        self._stopped = False

        # self.like_delay_sec = self.time_in_day / self.like_per_day_cap    part of LFS
        # self.follow_delay_sec = self.time_in_day / self.follow_per_day_cap  part of LFS

    def schedule_and_execute_actions_for_medias(self, medias):
        """
        :param medias:
        :type medias: list of instabotpatrik.model.InstagramMedia
        :return:
        """
        while len(medias) > 0 and self._stopped is False:
            try:
                self.logger.info("Handle media one by one by one: Some action should be possible now.")

                # ----- IF SCHEDULED: UNFOLLOW ------
                if self.action_manager.is_action_allowed_now("unfollow"):
                    self.logger.info("Going to unfollow someone.")
                    try:
                        self.unfollow_workflow.run()
                    finally:
                        self.action_manager.allow_action_after_seconds('unfollow', self.unfollow_delay_sec)

                # ----- IF SCHEDULED: LIKING SESSIONS------
                if self.action_manager.is_action_allowed_now("liking_session"):
                    media = medias.pop()
                    self.logger.info("Going to check if we can do LFS on media %s", media.shortcode)

                    # When tag is used by single owner, who is also not acceptable owner for LFS,
                    # we might get into a loop because all media codes we get are his. We should probably count
                    # how many times we tried to do LFS for a tag succesfully/unsucesfully and stored that information
                    # Then we can discover crappy tags and remove those.
                    # For now jsut workaround, put more sleep before doing next LFS checking
                    instabotpatrik.tools.go_sleep(duration_sec=30, plusminus=15)

                    # We could also do improvement here, we could track the last time we refreshed tht data
                    # and then refresh them only if certain amount time passed since last refresh
                    media_owner = self.user_controller.get_media_owner(media_shortcode=media.shortcode,
                                                                       asure_fresh_data=True)  # explore users profile
                    if self.lfs_workflow.is_approved_for_lfs(media_owner):
                        self.logger.info("Starting LFS on owner of media %s", media.shortcode)
                        try:
                            self.lfs_workflow.run(media, media_owner)
                        finally:
                            self.action_manager.allow_action_after_seconds('liking_session', self.unfollow_delay_sec)

                # ----- WAIT TILL NEXT ACTION------
                info = self.action_manager.seconds_left_until_some_action_possible()
                self.logger.info("Next possible action will be %s in %d seconds", info['action_name'],
                                 info['sec_left'])
                self.logger.info("Time left till next liking_session %d"
                                 % self.action_manager.seconds_left_until_action_possible("liking_session"))
                self.logger.info("Time left till next unfollow %d"
                                 % self.action_manager.seconds_left_until_action_possible("unfollow"))
                instabotpatrik.tools.go_sleep(duration_sec=info['sec_left'] + 20, plusminus=20)

            except instabotpatrik.client.InstagramResponseException as e:
                raise e
            except Exception as e:
                self.logger.error(e, exc_info=True)
                self.logger.error("Something went wrong. Will sleep 60 seconds")
                instabotpatrik.tools.go_sleep(duration_sec=120, plusminus=1)

    def run(self):
        self.logger.info("Starting bot with following configuration:")
        self.logger.info("Daily cap of LFS count:%d", self.lfs_per_day_cap)
        self.logger.info("Daily cap for unfollow count:%d", self.unfollow_per_day_cap)

        self.login_controller.login()

        while not self._stopped:
            try:
                self.current_tag = self.strategy_tag_selection.get_tag()
                self.logger.info("Starting main loop. Selected tag: %s", self.current_tag)
                our_username = self.login_controller.get_our_username()
                medias = self.media_controller.get_recent_media_by_tag(tag=self.current_tag,
                                                                       excluded_owner_usernames=[our_username])

                medias = random.sample(medias, int(len(medias) * self.select_ratio))

                self.logger.info("For tag %s was picked media: %s",
                                 self.current_tag, [media.shortcode for media in medias])

                self.schedule_and_execute_actions_for_medias(medias)

                self.logger.info("Runned out of all processed medias for tag %d", self.current_tag)
                instabotpatrik.tools.go_sleep(duration_sec=180, plusminus=120)

            except instabotpatrik.client.BottingDetectedException as e:
                self.logger.critical(e, exc_info=True)
                instabotpatrik.tools.go_sleep(duration_sec=self.ban_sleep_time_sec, plusminus=120)

            except instabotpatrik.client.UserNotFoundException as e:
                self.logger.warning(e, exc_info=True)
                self.user_controller.forget_user(username=e.username)

            except instabotpatrik.client.MediaNotFoundException as e:
                self.logger.warning(e, exc_info=True)
                self.media_controller.forget_media(shortcode=e.shortcode)

            except Exception as e:
                self.logger.error(e, exc_info=True)
                self.logger.error("Investigate this! Something went wrong")
                instabotpatrik.tools.go_sleep(duration_sec=self.ban_sleep_time_sec / 5, plusminus=120)

        self.logger.info("Bot is stopped.")

    def stop(self):
        self._stopped = True
        self.logger.info("Stopped flag was set.")
