from testsUnit.context import instabotpatrik
import logging
import unittest
import unittest.mock
import pymongo
from testsIntegrationDB import common

logging.getLogger().setLevel(30)


class CoreDBInteractionsTestCase(unittest.TestCase):
    def setUp(self):
        self.client_mock = unittest.mock.create_autospec(instabotpatrik.client.InstagramClient)
        self.config = common.get_config()
        self.mongo_client = pymongo.MongoClient(self.config.get_db_host(), self.config.get_db_port())
        self.repo_bot = common.create_repo(self.config, self.mongo_client)
        self.core = instabotpatrik.core.InstabotCore(self.repo_bot, self.client_mock)

    def tearDown(self):
        self.mongo_client.drop_database(self.config.get_db_name())


class ItShouldUpdateMediaInDBIfLiked(CoreDBInteractionsTestCase):
    def runTest(self):
        self.client_mock.like.return_value = True
        media1 = instabotpatrik.model.InstagramMedia(
            instagram_id="nn213b1jkbjk",
            shortcode="foobar42",
            owner_id="abcd1337",
            caption="awesome #cool",
            like_count=987,
            owner_username=None,
            is_liked=False,
            time_liked=None
        )

        self.assertFalse(media1.is_liked)
        self.core.like(media1)
        self.assertTrue(media1.is_liked)
        media_loaded = self.repo_bot.find_media_by_id("nn213b1jkbjk")

        self.assertEqual("nn213b1jkbjk", media_loaded.instagram_id)
        self.assertEqual("foobar42", media_loaded.shortcode)
        self.assertTrue(media_loaded.is_liked)


class ItShouldCreateUserIfNotStoredAndHisMediaWasLiked(CoreDBInteractionsTestCase):
    def runTest(self):
        self.client_mock.like.return_value = True
        media1 = instabotpatrik.model.InstagramMedia(
            instagram_id="nn213b1jkbjk",
            shortcode="foobar42",
            owner_id="abcd1337",
            caption="awesome #cool",
            like_count=987,
            owner_username=None,
            is_liked=False,
            time_liked=None
        )
        owner = instabotpatrik.model.InstagramUser(
            instagram_id="abcd1337",
            url="www.url.com",
            username="foouser",
            count_given_likes=10,
            count_shared_media=1,
            count_follows=2,
            count_followed_by=3,
            we_follow_user=True,
            user_follows_us=False
        )
        self.repo_bot.update_user(owner)
        self.core.like(media1)
        owner_user = self.repo_bot.find_user("abcd1337")

        self.assertEqual("abcd1337", owner_user.instagram_id)
        self.assertEqual(11, owner_user.count_given_likes)


class ItShouldUpdateExistingUserInDBWhoseMediaWasLiked(CoreDBInteractionsTestCase):
    def runTest(self):
        self.client_mock.like.return_value = True

        media1 = instabotpatrik.model.InstagramMedia(
            instagram_id="nn213b1jkbjk",
            shortcode="foobar42",
            owner_id="abcd1337",
            caption="awesome #cool",
            like_count=987,
            owner_username=None,
            is_liked=False,
            time_liked=None
        )

        self.core.like(media1)
        owner_user = self.repo_bot.find_user("abcd1337")

        self.assertEqual("abcd1337", owner_user.instagram_id)
        self.assertEqual(1, owner_user.count_given_likes)
