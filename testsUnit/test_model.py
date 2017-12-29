from testsUnit.context import instabotpatrik
import unittest.mock
import logging

logging.getLogger().setLevel(30)
logging.basicConfig(format='[%(levelname)s] [%(asctime)s] [%(name)s:%(funcName)s] : %(message)s',
                    datefmt='%m/%d/%Y-%H:%M:%S')


class UserDetailTestCase(unittest.TestCase):
    def setUp(self):
        self.original_history = instabotpatrik.model.InstagramUserBotData(count_likes_we_gave=10,
                                                                             last_like_datetime="timestamp1",
                                                                             last_follow_datetime="timestamp2",
                                                                             last_unfollow_datetime="timestamp3")
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
            bot_data=self.original_history
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

        self.assertEqual(self.user.url, self.new_version_user.url)
        self.assertEqual(self.user.count_shared_media, self.new_version_user.count_shared_media)
        self.assertEqual(self.user.count_follows, self.new_version_user.count_follows)
        self.assertEqual(self.user.count_followed_by, self.new_version_user.count_followed_by)
        self.assertEqual(self.user.we_follow_user, self.new_version_user.we_follow_user)


# TODO: This test look like code smell ...
class ItShouldNotMakeShallowCopyOfDetails(UserDetailTestCase):

    def runTest(self):
        self.user.update_details(self.new_version_user)

        self.assertNotEqual(self.user._detail, self.new_version_user._detail)


class ItShouldNotModifyBotHistory(UserDetailTestCase):

    def runTest(self):
        self.user.update_details(self.new_version_user)

        self.assertEqual(self.user.count_likes_we_gave, self.original_history.count_likes_we_gave)
        self.assertEqual(self.user.dt_like, self.original_history.dt_like)
        self.assertEqual(self.user.dt_follow, self.original_history.dt_follow)
        self.assertEqual(self.user.dt_unfollow, self.original_history.dt_unfollow)
