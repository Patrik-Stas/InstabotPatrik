from testsUnit.context import instabotpatrik
from testsUnit.context import testcommon
import logging
import unittest
import unittest.mock
import pymongo
from testsIntegrationDB import common
import datetime
import pytz
import freezegun

logging.getLogger().setLevel(30)


class CoreDBInteractionsTestCase(unittest.TestCase):
    def setUp(self):
        self.client_mock = unittest.mock.create_autospec(instabotpatrik.client.InstagramClient)
        self.config = common.get_config()
        self.mongo_client = pymongo.MongoClient(self.config.get_db_host(), self.config.get_db_port())
        self.mongo_client.drop_database(self.config.get_db_name())
        self.repo_bot = common.create_repo(self.config, self.mongo_client)
        self.user_controller = instabotpatrik.core.UserController(self.repo_bot, self.client_mock)

    def tearDown(self):
        self.mongo_client.drop_database(self.config.get_db_name())


class ItShouldUpdateExistingUserWhenMediaOwnerIsQueried(CoreDBInteractionsTestCase):
    def runTest(self):
        # prepare
        bot_data = instabotpatrik.model.InstagramUserBotData(
            count_likes_we_gave=10,
            last_like_datetime=datetime.datetime(year=2001, month=12, day=12, hour=12, tzinfo=pytz.UTC),
            last_follow_datetime=datetime.datetime(year=2002, month=12, day=12, hour=12, tzinfo=pytz.UTC)
        )
        user_no_details = instabotpatrik.model.InstagramUser("user_id", username="username1", bot_data=bot_data)
        api_user_detail = testcommon.factory.create_user_detail();
        api_user = instabotpatrik.model.InstagramUser("user_id", username="username1", user_detail=api_user_detail)
        media = instabotpatrik.model.InstagramMedia("media123", "code123", "user_id", "#caption",
                                                    owner_username="username1")
        self.repo_bot.update_user(user_no_details)
        self.client_mock.get_media_detail.return_value = media
        self.client_mock.get_user_with_details.return_value = api_user

        # exercise
        returned_user = self.user_controller.get_media_owner(media_shortcode="code123", asure_fresh_data=True)

        # verify
        self.assertEqual("user_id", returned_user.instagram_id)
        self.assertEqual("username1", returned_user.username)
        self.assertEqual(api_user_detail.url, returned_user.url)
        self.assertEqual(api_user_detail.count_shared_media, returned_user.count_shared_media)
        self.assertEqual(api_user_detail.count_follows, returned_user.count_follows)
        self.assertEqual(api_user_detail.count_followed_by, returned_user.count_followed_by)
        self.assertEqual(api_user_detail.we_follow_user, returned_user.we_follow_user)
        self.assertEqual(api_user_detail.user_follows_us, returned_user.user_follows_us)
        self.assertEqual(user_no_details.count_likes_we_gave, returned_user.count_likes_we_gave)
        self.assertEqual(user_no_details.dt_like, returned_user.dt_like)
        self.assertEqual(user_no_details.dt_follow, returned_user.dt_follow)
        self.assertEqual(user_no_details.dt_unfollow, returned_user.dt_unfollow)

        db_loaded_user = self.repo_bot.find_user("user_id")
        self.assertEqual("user_id", db_loaded_user.instagram_id)
        self.assertEqual("username1", db_loaded_user.username)
        self.assertEqual(api_user_detail.url, db_loaded_user.url)
        self.assertEqual(api_user_detail.count_shared_media, db_loaded_user.count_shared_media)
        self.assertEqual(api_user_detail.count_follows, db_loaded_user.count_follows)
        self.assertEqual(api_user_detail.count_followed_by, db_loaded_user.count_followed_by)
        self.assertEqual(api_user_detail.we_follow_user, db_loaded_user.we_follow_user)
        self.assertEqual(api_user_detail.user_follows_us, db_loaded_user.user_follows_us)
        self.assertEqual(user_no_details.count_likes_we_gave, db_loaded_user.count_likes_we_gave)
        self.assertEqual(user_no_details.dt_like, db_loaded_user.dt_like)
        self.assertEqual(user_no_details.dt_follow, db_loaded_user.dt_follow)
        self.assertEqual(user_no_details.dt_unfollow, db_loaded_user.dt_unfollow)


class ItShoulStoreUserIfDoesntExistsInDb(CoreDBInteractionsTestCase):
    def runTest(self):
        # prepare
        api_user_detail = testcommon.factory.create_user_detail();
        api_user = instabotpatrik.model.InstagramUser("user_id", username="username1", user_detail=api_user_detail)
        media = instabotpatrik.model.InstagramMedia("media123", "code123", "user_id", "#caption",
                                                    owner_username="username1")
        self.client_mock.get_media_detail.return_value = media
        self.client_mock.get_user_with_details.return_value = api_user

        # exercise
        user = self.user_controller.get_media_owner(media_shortcode="code123")

        # verify
        self.assertEqual("user_id", user.instagram_id)
        self.assertEqual("username1", user.username)
        self.assertEqual(api_user_detail.url, user.url)
        self.assertEqual(api_user_detail.count_shared_media, user.count_shared_media)
        self.assertEqual(api_user_detail.count_follows, user.count_follows)
        self.assertEqual(api_user_detail.count_followed_by, user.count_followed_by)
        self.assertEqual(api_user_detail.we_follow_user, user.we_follow_user)
        self.assertEqual(api_user_detail.user_follows_us, user.user_follows_us)
        self.assertEqual(None, user.count_likes_we_gave)
        self.assertEqual(None, user.dt_like)
        self.assertEqual(None, user.dt_follow)
        self.assertEqual(None, user.dt_unfollow)


class ItShouldUpdateUserWhenWeFollowUser(CoreDBInteractionsTestCase):
    @freezegun.freeze_time("2017-12-12 12:00:00", tz_offset=0)
    def runTest(self):
        user = common.get_sample_user(we_follow_user=False)
        self.assertEquals(user.we_follow_user, False)
        self.repo_bot.update_user(user)
        self.client_mock.like.return_value = True

        self.user_controller.follow(instagram_id=user.instagram_id)

        user_loaded = self.repo_bot.find_user_by_username("username")
        self.assertEquals(user.instagram_id, user_loaded.instagram_id)
        self.assertEquals(user.username, user_loaded.username)
        self.assertEquals(user.count_likes_we_gave, user_loaded.count_likes_we_gave)
        self.assertEquals(user.dt_like, user_loaded.dt_like)
        self.assertEquals(datetime.datetime(year=2017, month=12, day=12, hour=12, tzinfo=pytz.UTC),
                          user_loaded.dt_follow)
        self.assertEquals(user.dt_unfollow, user_loaded.dt_unfollow)
        self.assertEquals(user.url, user_loaded.url)
        self.assertEquals(user.count_shared_media, user_loaded.count_shared_media)
        self.assertEquals(user.count_follows, user_loaded.count_follows)
        self.assertEquals(user.count_followed_by, user_loaded.count_followed_by)
        self.assertEquals(True, user_loaded.we_follow_user)
        self.assertEquals(user.user_follows_us, user_loaded.user_follows_us)


class ItShouldUpdateUserWhenWeUnfollowUser(CoreDBInteractionsTestCase):
    @freezegun.freeze_time("2018-12-12 12:00:00", tz_offset=0)
    def runTest(self):
        user = common.get_sample_user(we_follow_user=True)
        self.assertEquals(user.we_follow_user, True)
        self.repo_bot.update_user(user)
        self.client_mock.like.return_value = True

        self.user_controller.unfollow(instagram_id=user.instagram_id)

        user_loaded = self.repo_bot.find_user_by_username("username")
        self.assertEquals(user.instagram_id, user_loaded.instagram_id)
        self.assertEquals(user.username, user_loaded.username)
        self.assertEquals(user.count_likes_we_gave, user_loaded.count_likes_we_gave)
        self.assertEquals(user.dt_like, user_loaded.dt_like)
        self.assertEquals(user.dt_follow, user_loaded.dt_follow)
        self.assertEquals(datetime.datetime(year=2018, month=12, day=12, hour=12, tzinfo=pytz.UTC),
                          user_loaded.dt_unfollow)
        self.assertEquals(user.url, user_loaded.url)
        self.assertEquals(user.count_shared_media, user_loaded.count_shared_media)
        self.assertEquals(user.count_follows, user_loaded.count_follows)
        self.assertEquals(user.count_followed_by, user_loaded.count_followed_by)
        self.assertEquals(False, user_loaded.we_follow_user)
        self.assertEquals(user.user_follows_us, user_loaded.user_follows_us)
