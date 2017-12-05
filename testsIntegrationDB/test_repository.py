# -*- coding: utf-8 -*-
from testsUnit.context import instabotpatrik
import logging
import unittest
import pymongo
import instabotpatrik.repository
import instabotpatrik.model
import time

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

        like_timestamp = time.time()
        user1_loaded.count_followed_by = 12321
        user1_loaded.user_follows_us = False
        user1_loaded.last_like_given_timestamp = like_timestamp
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
        self.assertEqual(user1_loaded.last_like_given_timestamp, like_timestamp)
        self.assertEqual(user1_loaded.last_follow_given_timestamp, None)
        self.assertEqual(user1_loaded.last_unfollow_given_timestamp, None)


class ItShouldSaveAndLoadUpdateMedia(unittest.TestCase):
    def test_run(self):
        mongo_client = pymongo.MongoClient('localhost', 27017)
        repository = instabotpatrik.repository.BotRepositoryMongoDb(mongo_client=mongo_client,
                                                                    database_name="test_instabotpat",
                                                                    users_collection_name="test_users",
                                                                    media_collection_name="test_media")
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
        repository.update_media(media1)
        media1_loaded = repository.load_media(instagram_id)

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

        # TODO: store timestamps in human readable format / load and parse into python time format
        # user1_loaded.add_follow(timestamp=time.time())
        repository.update_media(media1_loaded)
        media1_loaded2 = repository.load_media(instagram_id)

        self.assertEqual(media1_loaded2.instagram_id, media1.instagram_id)
        self.assertEqual(media1_loaded2.shortcode, media1.shortcode)
        self.assertEqual(media1_loaded2.owner_id, media1.owner_id)
        self.assertEqual(media1_loaded2.caption, "changedcaption")
        self.assertEqual(media1_loaded2.is_liked, True)
        self.assertEqual(media1_loaded2.like_count, media1.like_count)
        self.assertEqual(media1_loaded2.time_liked, media1.time_liked)
        self.assertEqual(media1_loaded2.owner_username, media1.owner_username)


class ItShouldSaveAndLoadUpdateMedia(unittest.TestCase):
    def test_run(self):
        mongo_client = pymongo.MongoClient('localhost', 27017)
        repository = instabotpatrik.repository.BotRepositoryMongoDb(mongo_client=mongo_client,
                                                                    database_name="test_instabotpat",
                                                                    users_collection_name="test_users",
                                                                    media_collection_name="test_media")
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
        repository.update_user(user1)
        repository.update_user(user2)
        repository.update_user(user3)
        followed = repository.find_followed_user()

        self.assertEquals(len(followed), 2)
