from testsUnit.context import instabotpatrik
import unittest.mock


class UserDetailTestCase(unittest.TestCase):
    def setUp(self):
        self.original_history = instabotpatrik.model.InstagramUserBotHistory(count_likes=10,
                                                                             last_like_timestamp="timestamp1",
                                                                             last_follow_timestamp="timestamp2",
                                                                             last_unfollow_timestamp="timestamp3")
        old_details = instabotpatrik.model.InstagramUserDetail(url="http://www.foo.com",
                                                               count_shared_media=1,
                                                               count_follows=2,
                                                               count_followed_by=3,
                                                               we_follow_user=False,
                                                               user_follows_us=False)
        self.user = instabotpatrik.model.InstagramUser(
            instagram_id="abcd1337",
            username="foouser",
            user_detail=old_details,
            bot_history=self.original_history
        )
        new_details = instabotpatrik.model.InstagramUserDetail(url="http://www.bar.com",
                                                               count_shared_media=100,
                                                               count_follows=200,
                                                               count_followed_by=300,
                                                               we_follow_user=True,
                                                               user_follows_us=True)
        self.new_version_user = instabotpatrik.model.InstagramUser(
            instagram_id="abcd1337",
            username="foouser",
            user_detail=new_details
        )


class ItShouldUpdateUserDetails(UserDetailTestCase):

    def runTest(self):
        self.user.update_details(self.new_version_user)

        self.assertEqual(self.user.detail.url, self.new_version_user.detail.url)
        self.assertEqual(self.user.detail.count_shared_media, self.new_version_user.detail.count_shared_media)
        self.assertEqual(self.user.detail.count_follows, self.new_version_user.detail.count_follows)
        self.assertEqual(self.user.detail.count_followed_by, self.new_version_user.detail.count_followed_by)
        self.assertEqual(self.user.detail.we_follow_user, self.new_version_user.detail.we_follow_user)


class ItShouldNotMakeShallowCopyOfDetails(UserDetailTestCase):

    def runTest(self):
        self.user.update_details(self.new_version_user)

        self.assertNotEqual(self.user.detail, self.new_version_user.detail)


class ItShouldNotModifyBotHistory(UserDetailTestCase):

    def runTest(self):
        self.user.update_details(self.new_version_user)

        self.assertEqual(self.user.bot_data.count_likes, self.original_history.count_likes)
        self.assertEqual(self.user.bot_data.last_like_timestamp, self.original_history.last_like_timestamp)
        self.assertEqual(self.user.bot_data.last_follow_timestamp, self.original_history.last_follow_timestamp)
        self.assertEqual(self.user.bot_data.last_unfollow_timestamp, self.original_history.last_unfollow_timestamp)
