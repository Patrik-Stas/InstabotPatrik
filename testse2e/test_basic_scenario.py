# -*- coding: utf-8 -*-
from testse2e.context import instabotpatrik
from testse2e import common
import unittest
import pymongo
import yaml
import os
import time
import logging
import subprocess
import requests

logging.getLogger().setLevel(20)
logging.basicConfig(format='[%(levelname)s] [%(asctime)s] [%(name)s:%(funcName)s] : %(message)s',
                    datefmt='%m/%d/%Y-%H:%M:%S')


class TestBasicScenario(unittest.TestCase):
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

    def drop_e2e_database(self):
        self.logger.info("E2E tearDown DB cleanup. Dropping database %s", self.config.get_db_name())
        self.mongo_client.drop_database(self.config.get_db_name())

    def init_e2e_database(self):
        self.logger.info("Going to intialize E2E testing database.")
        bash_command = "mongo --host %s --port %s %s" % \
                       (self.config.get_db_host(),
                        self.config.get_db_port(),
                        self.get_path_to_file_in_directory_of_this_file("db_e2e_init.js"))
        self.logger.info("Going to run bash command: %s", bash_command)
        process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        self.logger.info("Output from running e2e DB init script:\n%s" % output)
        self.logger.error("Errors from running e2e DB init script:\n%s" % output)
        if error is not None:
            raise Exception("Database initialization failed.")
        else:
            print("E2E testing database intialised")

    def setUp(self):
        print("Assure DB doesn't exists on start")
        self.logger = logging.getLogger(self.__class__.__name__)

        self.config = common.get_config()
        self.mongo_client = pymongo.MongoClient(self.config.get_db_host(), self.config.get_db_port())

        self.drop_e2e_database()  # Decide if you want to start over or continue ...
        self.init_e2e_database()

    def runTest(self):
        credentials = self.load_instagram_credentials()
        self.client = instabotpatrik.client.InstagramClient(
            user_login=credentials['user']['username'],
            user_password=credentials['user']['password'],
            requests_session=requests.Session(),
            try_to_load_session_from_file=True
        )
        bot_runner = instabotpatrik.runner.BasicSetup(cfg=self.config, api_client=self.client)

        self.logger.info("Let's login")
        bot_runner.account_controller.login()

        time.sleep(3)
        self.logger.info("Let's find some media by tag")
        medias = bot_runner.media_controller.get_recent_media_by_tag("nice")
        user_last_media1 = medias[0]

        time.sleep(3)
        self.logger.info("Let's get user which posted the last media for the tag")
        owner = bot_runner.user_controller.get_media_owner(media_shortcode=user_last_media1.shortcode, asure_fresh_data=True)
        bot_runner.api_client.unfollow(user_id=owner.instagram_id)  # send raw unfollow api call, just to make sure.

        self.assertIsNone(owner.dt_follow)
        self.assertIsNone(owner.dt_like)
        self.assertIsNone(owner.dt_unfollow)

        time.sleep(3)
        self.logger.info("Let's get recent media for this user")
        users_medias = bot_runner.media_controller.get_recent_media_for_user(owner.username)
        self.assertGreaterEqual(len(users_medias), 1)
        self.assertLessEqual(len(users_medias), 50)

        time.sleep(3)
        self.logger.info("Let's give a like for first media of this user")

        user_last_media1 = users_medias[0]
        datetime_before_like1 = instabotpatrik.tools.get_utc_datetime()
        bot_runner.media_controller.like(media_id=user_last_media1.instagram_id, shortcode=user_last_media1.shortcode)
        datetime_after_like1 = instabotpatrik.tools.get_utc_datetime()

        media_after_like1 = bot_runner.repo_bot.find_media_by_id(user_last_media1.instagram_id)
        self.assertTrue(media_after_like1.is_liked)
        self.assertTrue(datetime_before_like1 <= media_after_like1.time_liked <= datetime_after_like1)
        self.assertEqual(owner.instagram_id, media_after_like1.owner_id)
        self.assertEqual(owner.username, media_after_like1.owner_username)

        user_after_like = bot_runner.user_controller.get_user_by_id(instagram_id=owner.instagram_id)
        # currently we have get instance of this user again, freshly load from DB

        self.assertEqual(1, user_after_like.count_likes_we_gave)
        self.assertFalse(user_after_like.we_follow_user)
        self.assertIsNone(user_after_like.dt_unfollow)
        self.assertIsNone(user_after_like.dt_follow)
        self.assertTrue(datetime_before_like1 <= user_after_like.dt_like <= datetime_after_like1)

        time.sleep(3)
        self.logger.info("Let's give a like for second media of this user")

        user_last_media2 = users_medias[1]
        datetime_before_like2 = instabotpatrik.tools.get_utc_datetime()
        bot_runner.media_controller.like(media_id=user_last_media2.instagram_id, shortcode=user_last_media2.shortcode)
        datetime_after_like2 = instabotpatrik.tools.get_utc_datetime()

        media_after_like2 = bot_runner.repo_bot.find_media_by_id(user_last_media2.instagram_id)
        self.assertTrue(media_after_like2.is_liked)

        user_after_like2 = bot_runner.user_controller.get_user_by_id(instagram_id=owner.instagram_id)

        self.assertFalse(user_after_like.we_follow_user)
        self.assertTrue(datetime_before_like2 <= user_after_like2.dt_like <= datetime_after_like2)
        self.assertIsNone(user_after_like.dt_unfollow)
        self.assertIsNone(user_after_like.dt_follow)
        self.assertEqual(2, user_after_like2.count_likes_we_gave)

        time.sleep(3)
        self.logger.info("Let's follow the user now")

        datetime_before_follow = instabotpatrik.tools.get_utc_datetime()
        bot_runner.user_controller.follow(instagram_id=owner.instagram_id)
        datetime_after_follow = instabotpatrik.tools.get_utc_datetime()

        user_after_follow = bot_runner.user_controller.get_user_by_id(instagram_id=owner.instagram_id)

        self.assertTrue(user_after_follow.we_follow_user)
        self.assertTrue(datetime_before_like2 <= user_after_follow.dt_like <= datetime_after_like2)
        self.assertTrue(datetime_before_follow <= user_after_follow.dt_follow <= datetime_after_follow)
        self.assertIsNone(user_after_follow.dt_unfollow)
        self.assertEquals(2, user_after_like2.count_likes_we_gave)

        time.sleep(3)
        self.logger.info("Let's unfollow the user now")

        datetime_before_unfollow = instabotpatrik.tools.get_utc_datetime()
        bot_runner.user_controller.unfollow(instagram_id=owner.instagram_id)
        datetime_after_unfollow = instabotpatrik.tools.get_utc_datetime()

        user_after_unfollow = bot_runner.user_controller.get_user_by_id(instagram_id=owner.instagram_id)

        self.assertFalse(user_after_unfollow.we_follow_user)
        self.assertTrue(datetime_before_like2 <= user_after_unfollow.dt_like <= datetime_after_like2)
        self.assertTrue(datetime_before_follow <= user_after_unfollow.dt_follow <= datetime_after_follow)
        self.assertTrue(datetime_before_unfollow <= user_after_unfollow.dt_unfollow <= datetime_after_unfollow)
        self.assertEquals(2, user_after_like2.count_likes_we_gave)

