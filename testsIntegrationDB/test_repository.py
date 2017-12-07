# -*- coding: utf-8 -*-
from testsUnit.context import instabotpatrik
import logging
import unittest
import pymongo
import instabotpatrik.repository
import instabotpatrik.model
import time
import os
import yaml

logging.getLogger().setLevel(30)


# TODO: The test_config yaml stuff should go away, these values should be somehow injected into the test runner
# TODO: Also parametetrize test logging level

def get_path_to_file_in_directory_of_this_file(file_name):
    this_directory_absolute = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    return os.path.join(this_directory_absolute, file_name)


def load_test_configuration():
    with open(get_path_to_file_in_directory_of_this_file("test_config.yaml"), 'r') as stream:
        try:
            return yaml.load(stream)
        except yaml.YAMLError as exc:
            print(exc)


class ItShouldSaveAndLoadUpdateUser(unittest.TestCase):

    def setUp(self):
        self.config = load_test_configuration()

    def tearDown(self):
        self.mongo_client.drop_database(self.config['database']['name'])

    def test_run(self):
        self.mongo_client = pymongo.MongoClient('localhost', 27017)
        repository = instabotpatrik.repository.BotRepositoryMongoDb(mongo_client=self.mongo_client,
                                                                    database_name=self.config['database']['name'],
                                                                    users_collection_name=self.config['database'][
                                                                        'collection_users'],
                                                                    media_collection_name=self.config['database'][
                                                                        'collection_media'])
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
        repository.update_user(user1)
        user1_loaded = repository.find_user_by_instagram_id(instagram_id)

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
        repository.update_user(user1_loaded)

        user1_loaded2 = repository.find_user_by_instagram_id(instagram_id)

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


class ItShouldSaveAndLoadUpdateMedia(unittest.TestCase):
    def setUp(self):
        self.config = load_test_configuration()

    def tearDown(self):
        self.mongo_client.drop_database(self.config['database']['name'])

    def test_run(self):
        self.mongo_client = pymongo.MongoClient('localhost', 27017)
        repository = instabotpatrik.repository.BotRepositoryMongoDb(mongo_client=self.mongo_client,
                                                                    database_name=self.config['database']['name'],
                                                                    users_collection_name=self.config['database'][
                                                                        'collection_users'],
                                                                    media_collection_name=self.config['database'][
                                                                        'collection_media'])
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
        media1_loaded = repository.find_media_by_id(instagram_id)

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

        repository.update_media(media1_loaded)
        media1_loaded2 = repository.find_media_by_id(instagram_id)

        self.assertEqual(media1_loaded2.instagram_id, media1.instagram_id)
        self.assertEqual(media1_loaded2.shortcode, media1.shortcode)
        self.assertEqual(media1_loaded2.owner_id, media1.owner_id)
        self.assertEqual(media1_loaded2.caption, "changedcaption")
        self.assertEqual(media1_loaded2.is_liked, True)
        self.assertEqual(media1_loaded2.like_count, media1.like_count)
        self.assertEqual(media1_loaded2.time_liked, media1.time_liked)
        self.assertEqual(media1_loaded2.owner_username, media1.owner_username)


class ItShouldFindUserFollowedUsers(unittest.TestCase):
    def setUp(self):
        self.config = load_test_configuration()

    def tearDown(self):
        self.mongo_client.drop_database(self.config['database']['name'])

    def test_run(self):
        self.mongo_client = pymongo.MongoClient('localhost', 27017)
        repository = instabotpatrik.repository.BotRepositoryMongoDb(mongo_client=self.mongo_client,
                                                                    database_name=self.config['database']['name'],
                                                                    users_collection_name=self.config['database'][
                                                                        'collection_users'],
                                                                    media_collection_name=self.config['database'][
                                                                        'collection_media'])
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
        followed = repository.find_followed_users()

        self.assertEqual(len(followed), 2)
        self.assertTrue("xyz" in [user.instagram_id for user in followed])
        self.assertTrue("foouser" in [user.instagram_id for user in followed])
