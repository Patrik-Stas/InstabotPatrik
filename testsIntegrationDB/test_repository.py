# -*- coding: utf-8 -*-
from testsUnit.context import instabotpatrik
import logging
import unittest
import pymongo
import instabotpatrik.repository
import instabotpatrik.model
import time
from testsIntegrationDB import common

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
            url="www.url.com",
            username="username1234xyz",
            count_shared_media=1,
            count_follows=2,
            count_followed_by=3,
            we_follow_user=False,
            user_follows_us=True,
            count_given_likes=12
        )
        self.repository.update_user(user1)
        user1_loaded = self.repository.find_user(instagram_id)

        self.assertEqual(user1_loaded.instagram_id, user1.instagram_id)
        self.assertEqual(user1_loaded.url, user1.url)
        self.assertEqual(user1_loaded.username, user1.username)
        self.assertEqual(user1_loaded.count_shared_media, user1.count_shared_media)
        self.assertEqual(user1_loaded.count_follows, user1.count_follows)
        self.assertEqual(user1_loaded.count_followed_by, user1.count_followed_by)
        self.assertEqual(user1_loaded.count_given_likes, user1.count_given_likes)
        self.assertEqual(user1_loaded.we_follow_user, user1.we_follow_user)
        self.assertEqual(user1_loaded.user_follows_us, user1.user_follows_us)
        self.assertEqual(user1_loaded.last_like_given_timestamp, None)
        self.assertEqual(user1_loaded.last_follow_given_timestamp, None)
        self.assertEqual(user1_loaded.last_unfollow_given_timestamp, None)

        like_timestamp = time.time()
        user1_loaded.count_followed_by = 12321
        user1_loaded.user_follows_us = False
        user1_loaded.last_like_given_timestamp = like_timestamp
        self.repository.update_user(user1_loaded)

        user1_loaded2 = self.repository.find_user(instagram_id)

        self.assertEqual(user1_loaded2.instagram_id, user1.instagram_id)
        self.assertEqual(user1_loaded2.url, user1.url)
        self.assertEqual(user1_loaded2.username, user1.username)
        self.assertEqual(user1_loaded2.count_shared_media, user1.count_shared_media)
        self.assertEqual(user1_loaded2.count_follows, user1.count_follows)
        self.assertEqual(user1_loaded2.count_followed_by, 12321)
        self.assertEqual(user1_loaded2.we_follow_user, user1.we_follow_user)
        self.assertEqual(user1_loaded2.user_follows_us, False)
        self.assertEqual(user1_loaded2.last_like_given_timestamp, like_timestamp)
        self.assertEqual(user1_loaded2.last_follow_given_timestamp, None)
        self.assertEqual(user1_loaded2.last_unfollow_given_timestamp, None)
        self.assertEqual(user1_loaded2.count_given_likes, user1.count_given_likes)


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
            time_liked=time.time()
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
            url="www.url.com",
            username="abcuser",
            count_shared_media=1,
            count_follows=2,
            count_followed_by=3,
            we_follow_user=False,
            user_follows_us=True
        )
        user2 = instabotpatrik.model.InstagramUser(
            instagram_id="xyz",
            url="www.url.com",
            username="xyzuser",
            count_shared_media=1,
            count_follows=2,
            count_followed_by=3,
            we_follow_user=True,
            user_follows_us=True
        )
        user3 = instabotpatrik.model.InstagramUser(
            instagram_id="foouser",
            url="www.url.com",
            username="foouser",
            count_shared_media=1,
            count_follows=2,
            count_followed_by=3,
            we_follow_user=True,
            user_follows_us=False
        )
        self.repository.update_user(user1)
        self.repository.update_user(user2)
        self.repository.update_user(user3)
        followed = self.repository.find_followed_users()

        self.assertEqual(len(followed), 2)
        self.assertTrue("xyz" in [user.instagram_id for user in followed])
        self.assertTrue("foouser" in [user.instagram_id for user in followed])
