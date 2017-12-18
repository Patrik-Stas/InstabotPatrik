# -*- coding: utf-8 -*-
from testsIntegrationDB.context import instabotpatrik
from testsIntegrationDB.context import testcommon
import logging
import unittest
import pymongo
import instabotpatrik.repository
import instabotpatrik.model
import datetime
from testsIntegrationDB import common
import pytz

logging.getLogger().setLevel(30)


class RepositoryTestCase(unittest.TestCase):
    def setUp(self):
        self.config = common.get_config()
        self.mongo_client = pymongo.MongoClient('localhost', 27017)
        self.repository = common.create_repo(self.config, self.mongo_client)

    def tearDown(self):
        self.mongo_client.drop_database(self.config.get_db_name())


class ItShouldSaveAndLoadUpdateUser(RepositoryTestCase):

    def test_run(self):
        instagram_id = "nn213b1jkbjk"
        user1 = instabotpatrik.model.InstagramUser(
            instagram_id=instagram_id,
            username="username1234xyz",
            user_detail=testcommon.factory.create_user_detail()
        )
        self.repository.update_user(user1)
        user1_loaded = self.repository.find_user(instagram_id)

        self.assertEqual(user1_loaded.instagram_id, user1.instagram_id)
        self.assertEqual(user1_loaded.username, user1.username)

        self.assertEqual(user1_loaded.detail.url, user1.detail.url)
        self.assertEqual(user1_loaded.detail.count_shared_media, user1.detail.count_shared_media)
        self.assertEqual(user1_loaded.detail.count_follows, user1.detail.count_follows)
        self.assertEqual(user1_loaded.detail.count_followed_by, user1.detail.count_followed_by)
        self.assertEqual(user1_loaded.detail.we_follow_user, user1.detail.we_follow_user)
        self.assertEqual(user1_loaded.detail.user_follows_us, user1.detail.user_follows_us)

        self.assertEqual(user1_loaded.bot_data.count_likes, None)
        self.assertEqual(user1_loaded.bot_data.last_like_timestamp, None)
        self.assertEqual(user1_loaded.bot_data.last_follow_timestamp, None)
        self.assertEqual(user1_loaded.bot_data.last_unfollow_timestamp, None)

        like_timestamp = datetime.datetime.now(pytz.UTC)
        user1_loaded.detail.count_followed_by = 12321
        user1_loaded.detail.user_follows_us = False
        user1_loaded.bot_data.last_like_timestamp = like_timestamp
        self.repository.update_user(user1_loaded)

        user1_loaded2 = self.repository.find_user(instagram_id)

        self.assertEqual(user1_loaded2.instagram_id, user1.instagram_id)
        self.assertEqual(user1_loaded2.username, user1.username)

        self.assertEqual(user1_loaded2.detail.url, user1.detail.url)
        self.assertEqual(user1_loaded2.detail.count_shared_media, user1.detail.count_shared_media)
        self.assertEqual(user1_loaded2.detail.count_follows, user1.detail.count_follows)
        self.assertEqual(user1_loaded2.detail.count_followed_by, 12321)
        self.assertEqual(user1_loaded2.detail.we_follow_user, user1.detail.we_follow_user)
        self.assertEqual(user1_loaded2.detail.user_follows_us, False)

        self.assertEqual(user1_loaded2.bot_data.count_likes, user1.bot_data.count_likes)
        self.assertEqual(user1_loaded2.bot_data.last_like_timestamp, like_timestamp)
        self.assertEqual(user1_loaded2.bot_data.last_follow_timestamp, None)
        self.assertEqual(user1_loaded2.bot_data.last_unfollow_timestamp, None)


class ItShouldSaveAndLoadUpdateMedia(RepositoryTestCase):
    def test_run(self):
        instagram_id = "nn213b1jkbjk"
        media1 = instabotpatrik.model.InstagramMedia(
            instagram_id=instagram_id,
            shortcode="foobar42",
            owner_id="abcd1337",
            caption="awesome #cool",
            like_count=987,
            owner_username="user12",
            is_liked=False,
            time_liked=datetime.datetime.now(pytz.UTC)
        )
        self.repository.update_media(media1)
        media1_loaded = self.repository.find_media_by_id(instagram_id)

        self.assertEqual(media1_loaded.instagram_id, media1.instagram_id)
        self.assertEqual(media1_loaded.shortcode, media1.shortcode)
        self.assertEqual(media1_loaded.owner_id, media1.owner_id)
        self.assertEqual(media1_loaded.caption, media1.caption)
        self.assertEqual(media1_loaded.is_liked, media1.is_liked)
        self.assertEqual(media1_loaded.like_count, media1.like_count)
        self.assertEqual(media1_loaded.time_liked, media1.time_liked)
        self.assertEqual(media1_loaded.owner_username, media1.owner_username)

        media1_loaded.is_liked = True
        media1_loaded.caption = "changedcaption"

        self.repository.update_media(media1_loaded)
        media1_loaded2 = self.repository.find_media_by_id(instagram_id)

        self.assertEqual(media1_loaded2.instagram_id, media1.instagram_id)
        self.assertEqual(media1_loaded2.shortcode, media1.shortcode)
        self.assertEqual(media1_loaded2.owner_id, media1.owner_id)
        self.assertEqual(media1_loaded2.caption, "changedcaption")
        self.assertEqual(media1_loaded2.is_liked, True)
        self.assertEqual(media1_loaded2.like_count, media1.like_count)
        self.assertEqual(media1_loaded2.time_liked, media1.time_liked)
        self.assertEqual(media1_loaded2.owner_username, media1.owner_username)


class ItShouldFindUserFollowedUsers(RepositoryTestCase):
    def runTest(self):
        user1 = instabotpatrik.model.InstagramUser(
            instagram_id="abc",
            username="abcuser",
            user_detail=testcommon.factory.create_user_detail(we_follow_user=False, user_follows_us=False)
        )
        user2 = instabotpatrik.model.InstagramUser(
            instagram_id="xyz",
            username="xyzuser",
            user_detail=testcommon.factory.create_user_detail(we_follow_user=True, user_follows_us=False)
        )
        user3 = instabotpatrik.model.InstagramUser(
            instagram_id="foo",
            username="foouser",
            user_detail=testcommon.factory.create_user_detail(we_follow_user=True, user_follows_us=False)
        )
        user4 = instabotpatrik.model.InstagramUser(
            instagram_id="bar",
            username="baruser",
        )
        self.repository.update_user(user1)
        self.repository.update_user(user2)
        self.repository.update_user(user3)
        self.repository.update_user(user4)
        followed = self.repository.find_followed_users()

        self.assertEqual(len(followed), 2)
        self.assertTrue("xyz" in [user.instagram_id for user in followed])
        self.assertTrue("foo" in [user.instagram_id for user in followed])
