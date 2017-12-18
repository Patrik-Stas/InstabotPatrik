from testsUnit.context import instabotpatrik
import logging
import unittest
import unittest.mock
import pymongo
from testsIntegrationDB import common
import datetime
import pytz

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


class ItShouldUpdateExistingUserInDBWhoseMediaWasLiked(CoreDBInteractionsTestCase):
    @unittest.mock.patch('instabotpatrik.tools')
    def runTest(self, mock_tools):
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
        detail = instabotpatrik.model.InstagramUserDetail(
            url="www.foo.bar",
            count_shared_media=1,
            count_follows=2,
            count_followed_by=3,
            we_follow_user=True,
            user_follows_us=False
        )
        bot_data = instabotpatrik.model.InstagramUserBotHistory(
            count_likes=10,
            last_like_timestamp=None,
            last_follow_timestamp=None,
            last_unfollow_timestamp=None)
        owner = instabotpatrik.model.InstagramUser(
            instagram_id="abcd1337",
            username="foouser",
            user_detail=detail,
            bot_history=bot_data
        )
        self.client_mock.like.return_value = True
        self.repo_bot.update_user(owner)
        like_time = datetime.datetime.now(pytz.UTC)
        mock_tools.get_utc_datetime.return_value = like_time

        self.core.like(media1)

        owner_user = self.repo_bot.find_user("abcd1337")
        self.assertEqual("abcd1337", owner_user.instagram_id)
        self.assertEqual(11, owner_user.bot_data.count_likes)
        self.assertEqual(like_time, owner_user.bot_data.last_like_timestamp)


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

        self.core.like(media1)
        owner_user = self.repo_bot.find_user("abcd1337")

        self.assertEqual("abcd1337", owner_user.instagram_id)
        self.assertEqual(1, owner_user.bot_data.count_likes)


# class GetMediaOwnerShouldUpdateUserDetailsInDatabase(CoreDBInteractionsTestCase):
#     def runTest(self):
#         user_in_db = instabotpatrik.model.InstagramUser("abcd1337")
#         self.repo_bot.update_user(user_in_db)
#
#         user_api_returned = instabotpatrik.model.InstagramUser(
#             instagram_id="abcd1337",
#             url="www.url.com",
#             username="foouser",
#             count_likes=10,
#             count_shared_media=1,
#             count_follows=2,
#             count_followed_by=3,
#             we_follow_user=True,
#             user_follows_us=False
#         )
#         self.client_mock.follow.return_value = True
#         self.client_mock.
#
#         self.core.get_media_owner(media)
#         owner_user = self.repo_bot.find_user("abcd1337")
#
#         self.assertEqual("abcd1337", owner_user.instagram_id)
#         self.assertEqual(1, owner_user.count_likes)

def get_sample_user(*args, **kwargs):
    detail = instabotpatrik.model.InstagramUserDetail(
        url="www.foo.bar",
        count_shared_media=1,
        count_follows=2,
        count_followed_by=3,
        we_follow_user=True,
        user_follows_us=False
    )
    user = instabotpatrik.model.InstagramUser(
        instagram_id="user1337",
        username="username1337",
        user_detail=detail
    )
    return user


class ItShouldUpdateDbWhenNewUserInformationAvailable(CoreDBInteractionsTestCase):
    def runTest(self):
        # prepare
        bot_data = instabotpatrik.model.InstagramUserBotHistory(
            count_likes=10,
            last_like_timestamp=None,
            last_follow_timestamp=None,
            last_unfollow_timestamp=None
        )
        self.repo_bot.update_user(instabotpatrik.model.InstagramUser("user1337", bot_history=bot_data))
        media_mock = instabotpatrik.model.InstagramMedia("media123", "code123", "user1337", "#caption")
        # media_mock.owner_id.return_value = "user1337"
        self.client_mock.get_user_with_details.side_effect = get_sample_user

        # exercise
        user = self.core.get_media_owner(media_mock)

        # verify
        db_user = self.repo_bot.find_user("user1337")
        self.assertEqual(user.instagram_id, db_user.instagram_id)
        self.assertEqual(user.username, db_user.username)
        self.assertEqual(user.detail.url, db_user.detail.url)
        self.assertEqual(user.detail.count_shared_media, db_user.detail.count_shared_media)
        self.assertEqual(user.detail.count_follows, db_user.detail.count_follows)
        self.assertEqual(user.detail.count_followed_by, db_user.detail.count_followed_by)
        self.assertEqual(user.detail.we_follow_user, db_user.detail.we_follow_user)
        self.assertEqual(user.detail.user_follows_us, db_user.detail.user_follows_us)
        self.assertEqual(user.bot_data.count_likes, db_user.bot_data.count_likes)
        self.assertEqual(user.bot_data.last_like_timestamp, db_user.bot_data.last_like_timestamp)
        self.assertEqual(user.bot_data.last_follow_timestamp, db_user.bot_data.last_follow_timestamp)
        self.assertEqual(user.bot_data.last_unfollow_timestamp, db_user.bot_data.last_unfollow_timestamp)
