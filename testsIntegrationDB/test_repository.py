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
import freezegun

logging.getLogger().setLevel(30)
logging.basicConfig(format='[%(levelname)s] [%(asctime)s] [%(name)s:%(funcName)s] : %(message)s',
                    datefmt='%m/%d/%Y-%H:%M:%S')


class RepositoryTestCase(unittest.TestCase):
    def setUp(self):
        self.config = common.get_config()
        self.mongo_client = pymongo.MongoClient('localhost', 27017)
        self.mongo_client.drop_database(self.config.get_db_name())
        self.repository = common.create_repo(self.config, self.mongo_client)

    def tearDown(self):
        self.mongo_client.drop_database(self.config.get_db_name())


class ItShouldSaveAndLoadUpdateUser(RepositoryTestCase):

    @freezegun.freeze_time("2011-11-11 11:11:00", tz_offset=0)
    def test_run(self):
        instagram_id = "nn213b1jkbjk"
        user1 = instabotpatrik.model.InstagramUser(
            instagram_id=instagram_id,
            username="username1234xyz",
            user_detail=testcommon.factory.create_user_detail(count_followed_by=123)
        )
        self.repository.update_user(user1)
        user1_loaded = self.repository.find_user(instagram_id)

        self.assertEqual(user1.instagram_id, user1_loaded.instagram_id)
        self.assertEqual(user1.username, user1_loaded.username)

        self.assertEqual(user1.url, user1_loaded.url)
        self.assertEqual(user1.count_shared_media, user1_loaded.count_shared_media)
        self.assertEqual(user1.count_follows, user1_loaded.count_follows)
        self.assertEqual(user1.count_followed_by, user1_loaded.count_followed_by)
        self.assertEqual(user1.we_follow_user, user1_loaded.we_follow_user)
        self.assertEqual(user1.user_follows_us, user1_loaded.user_follows_us)

        self.assertEqual(None, user1_loaded.count_likes_we_gave)
        self.assertEqual(None, user1_loaded.dt_like)
        self.assertEqual(None, user1_loaded.dt_follow)
        self.assertEqual(None, user1_loaded.dt_unfollow)

        user1_loaded.register_like()
        user1_loaded.register_follow()
        self.repository.update_user(user1_loaded)

        user1_loaded2 = self.repository.find_user(instagram_id)

        self.assertEqual(user1_loaded2.instagram_id, user1.instagram_id)
        self.assertEqual(user1_loaded2.username, user1.username)

        self.assertEqual(user1.url, user1_loaded2.url)
        self.assertEqual(user1.count_shared_media, user1_loaded2.count_shared_media)
        self.assertEqual(user1.count_follows, user1_loaded2.count_follows)
        self.assertEqual(123, user1_loaded2.count_followed_by)
        self.assertEqual(user1.we_follow_user, user1_loaded2.we_follow_user)
        self.assertEqual(False, user1_loaded2.user_follows_us)

        self.assertEqual(1, user1_loaded2.count_likes_we_gave)
        self.assertEqual(datetime.datetime(2011, 11, 11, 11, 11, 0, tzinfo=pytz.UTC), user1_loaded2.dt_like)
        self.assertEqual(datetime.datetime(2011, 11, 11, 11, 11, 0, tzinfo=pytz.UTC), user1_loaded2.dt_follow)
        self.assertEqual(None, user1_loaded2.dt_unfollow)


class ItShouldSaveAndLoadUpdateMedia(RepositoryTestCase):

    @freezegun.freeze_time("2012-10-12 13:00:00", tz_offset=0)
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
            time_liked=None
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

        media1_loaded.add_like()
        self.repository.update_media(media1_loaded)
        media1_loaded2 = self.repository.find_media_by_id(instagram_id)

        self.assertEqual(media1_loaded2.instagram_id, media1.instagram_id)
        self.assertEqual(media1_loaded2.shortcode, media1.shortcode)
        self.assertEqual(media1_loaded2.owner_id, media1.owner_id)
        self.assertEqual(media1_loaded2.caption, media1.caption)
        self.assertEqual(media1_loaded2.is_liked, True)
        self.assertEqual(media1_loaded2.like_count, media1.like_count)
        self.assertEqual(media1_loaded2.time_liked, datetime.datetime(2012, 10, 12, 13, 0, 0, tzinfo=pytz.UTC))
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
