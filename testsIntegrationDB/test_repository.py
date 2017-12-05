# -*- coding: utf-8 -*-
from testsUnit.context import instabotpatrik
import logging
import unittest
import pymongo
import instabotpatrik.repository
import instabotpatrik.model

logging.getLogger().setLevel(30)


class ItShouldSaveAndLoadUpdateUser(unittest.TestCase):
    def test_run(self):
        mongo_client = pymongo.MongoClient('localhost', 27017)
        repository = instabotpatrik.repository.BotRepositoryMongoDb(mongo_client=mongo_client,
                                                                    database_name="test_instabotpat",
                                                                    users_collection_name="test_users",
                                                                    media_collection_name="test_media")
        instagram_id = "nn213b1jkbjk"
        user1 = instabotpatrik.model.InstagramUser(
            instagram_id=instagram_id,
            url="www.url.com",
            username="username1234xyz",
            count_shared_media=1,
            count_follows=2,
            count_followed_by=3,
            we_follow_user=False,
            user_follows_us=True
        )
        repository.update_user(user1)
        user1_loaded = repository.load_user_by_instagram_id(instagram_id)

        self.assertEqual(user1_loaded.instagram_id, user1.instagram_id)
        self.assertEqual(user1_loaded.url, user1.url)
        self.assertEqual(user1_loaded.username, user1.username)
        self.assertEqual(user1_loaded.count_shared_media, user1.count_shared_media)
        self.assertEqual(user1_loaded.count_follows, user1.count_follows)
        self.assertEqual(user1_loaded.count_followed_by, user1.count_followed_by)
        self.assertEqual(user1_loaded.we_follow_user, user1.we_follow_user)
        self.assertEqual(user1_loaded.user_follows_us, user1.user_follows_us)
        self.assertEqual(user1_loaded.last_like_given_timestamp, None)
        self.assertEqual(user1_loaded.last_follow_given_timestamp, None)
        self.assertEqual(user1_loaded.last_unfollow_given_timestamp, None)

        user1_loaded.count_followed_by = 12321
        user1_loaded.user_follows_us = False
        repository.update_user(user1_loaded)

        user1_loaded2 = repository.load_user_by_instagram_id(instagram_id)

        self.assertEqual(user1_loaded2.instagram_id, user1.instagram_id)
        self.assertEqual(user1_loaded2.url, user1.url)
        self.assertEqual(user1_loaded2.username, user1.username)
        self.assertEqual(user1_loaded2.count_shared_media, user1.count_shared_media)
        self.assertEqual(user1_loaded2.count_follows, user1.count_follows)
        self.assertEqual(user1_loaded2.count_followed_by, 12321)
        self.assertEqual(user1_loaded2.we_follow_user, user1.we_follow_user)
        self.assertEqual(user1_loaded2.user_follows_us, False)

