from testsUnit.context import instabotpatrik
import logging
import unittest
import unittest.mock
import pymongo
from testsIntegrationDB import common
import datetime
import pytz
import freezegun

logging.getLogger().setLevel(30)
logging.basicConfig(format='[%(levelname)s] [%(asctime)s] [%(name)s:%(funcName)s] : %(message)s',
                    datefmt='%m/%d/%Y-%H:%M:%S')


class CoreDBInteractionsTestCase(unittest.TestCase):
    def setUp(self):
        self.client_mock = unittest.mock.create_autospec(instabotpatrik.client.InstagramClient)
        self.config = common.get_config()
        self.mongo_client = pymongo.MongoClient(self.config.get_db_host(), self.config.get_db_port())
        self.mongo_client.drop_database(self.config.get_db_name())
        self.repo_bot = common.create_repo(self.config, self.mongo_client)
        self.core = instabotpatrik.core.UserController(self.repo_bot, self.client_mock)
        self.media_controller = instabotpatrik.core.MediaController(self.repo_bot, self.client_mock)

    def tearDown(self):
        self.mongo_client.drop_database(self.config.get_db_name())


class ItShouldUpdateUserWhenWeLikeHisMedia(CoreDBInteractionsTestCase):
    @freezegun.freeze_time("2017-11-11 11:00:00", tz_offset=0)
    def runTest(self):
        user = common.get_sample_user()
        self.repo_bot.update_user(user)
        media1 = instabotpatrik.model.InstagramMedia(
            instagram_id="nn213b1jkbjk",
            shortcode="foobar42",
            caption="awesome #cool",
            like_count=987,
            owner_id="user_id",
            owner_username="username",
            is_liked=False,
            time_liked=None
        )
        self.repo_bot.update_media(media1)
        self.client_mock.like.return_value = True

        self.media_controller.like(media_id=media1.instagram_id, shortcode=media1.shortcode)

        user_loaded = self.repo_bot.find_user_by_username("username")
        self.assertEqual(user.instagram_id, user_loaded.instagram_id)
        self.assertEqual(user.username, user_loaded.username)
        self.assertEqual(user.count_likes_we_gave + 1, user_loaded.count_likes_we_gave)
        self.assertEqual(datetime.datetime(year=2017, month=11, day=11, hour=11, tzinfo=pytz.UTC), user_loaded.dt_like)
        self.assertEqual(user.dt_follow, user_loaded.dt_follow)
        self.assertEqual(user.dt_unfollow, user_loaded.dt_unfollow)
        self.assertEqual(user.url, user_loaded.url)
        self.assertEqual(user.count_shared_media, user_loaded.count_shared_media)
        self.assertEqual(user.count_follows, user_loaded.count_follows)
        self.assertEqual(user.count_followed_by, user_loaded.count_followed_by)
        self.assertEqual(user.we_follow_user, user_loaded.we_follow_user)
        self.assertEqual(user.user_follows_us, user_loaded.user_follows_us)


class ItShouldUpdateMediaInDbWhenIsLiked(CoreDBInteractionsTestCase):
    @freezegun.freeze_time("2017-10-10 10:00:00", tz_offset=0)
    def runTest(self):
        media1 = instabotpatrik.model.InstagramMedia(
            instagram_id="nn213b1jkbjk",
            shortcode="foobar42",
            caption="awesome #cool",
            like_count=987,
            owner_id="user_id",
            owner_username="username",
            is_liked=False,
            time_liked=None
        )
        self.repo_bot.update_media(media1)
        self.client_mock.like.return_value = True

        self.assertFalse(media1.is_liked)
        self.media_controller.like(media_id=media1.instagram_id, shortcode=media1.shortcode)
        media1 = self.repo_bot.find_media_by_id(media1.instagram_id)
        self.assertTrue(media1.is_liked)
        media_loaded = self.repo_bot.find_media_by_id("nn213b1jkbjk")

        self.assertEqual("nn213b1jkbjk", media_loaded.instagram_id)
        self.assertEqual("foobar42", media_loaded.shortcode)
        self.assertEqual(datetime.datetime(year=2017, month=10, day=10, hour=10, tzinfo=pytz.UTC),
                         media_loaded.time_liked)
        self.assertTrue(media_loaded.is_liked)


class ItShouldCorrectlyTrackNumberOfLikedMediasOfUser(CoreDBInteractionsTestCase):
    def runTest(self):
        media1 = instabotpatrik.model.InstagramMedia(
            instagram_id="mediaid1",
            shortcode="shortcode1",
            owner_id="owner_id1",
            caption="#foo"
        )
        media2 = instabotpatrik.model.InstagramMedia(
            instagram_id="mediaid2",
            shortcode="shortcode2",
            owner_id="owner_id1",
            caption="#foo"
        )
        self.repo_bot.update_media(media1)
        self.repo_bot.update_media(media2)

        self.media_controller.like(media_id=media1.instagram_id, shortcode=media1.shortcode)
        user_load1 = self.core.get_user_by_id("owner_id1")
        self.assertEqual(user_load1.count_likes_we_gave, 1)

        self.media_controller.like(media_id=media2.instagram_id, shortcode=media2.shortcode)
        self.media_controller.like(media_id=media2.instagram_id, shortcode=media2.shortcode)

        user_load2 = self.core.get_user_by_id("owner_id1")
        self.assertEqual(user_load2.count_likes_we_gave, 2)


class ItShouldQueryInstagramIfMediaIsNotStoredInDB(CoreDBInteractionsTestCase):
    def runTest(self):
        self.client_mock.like.return_value = True
        media1 = instabotpatrik.model.InstagramMedia(
            instagram_id="nonexisting_id",
            shortcode="foobar42",
            owner_id="nonexisting_username",
            caption="awesome #cool",
            like_count=987,
            owner_username=None,
            is_liked=False,
            time_liked=None
        )

        self.client_mock.get_media_detail.return_value = media1
        self.client_mock.like.return_value = True
        self.media_controller.like(media_id=media1.instagram_id, shortcode=media1.shortcode)

        self.client_mock.get_media_detail.assert_called_with(media1.shortcode)
        media_db = self.repo_bot.find_media_by_id(media_id=media1.instagram_id)
        self.assertEqual(media1.instagram_id, media_db.instagram_id)
        self.assertEqual(media1.shortcode, media_db.shortcode)
        self.assertEqual(media1.owner_id, media_db.owner_id)
        self.assertEqual(media1.caption, media_db.caption)
        self.assertEqual(media1.like_count, media_db.like_count)
        self.assertEqual(media1.owner_username, media_db.owner_username)
        self.assertTrue(media_db.is_liked)
