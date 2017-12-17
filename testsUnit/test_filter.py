from testsUnit.context import instabotpatrik
from testsUnit.context import testcommon
import unittest.mock
import logging
import datetime

logging.getLogger().setLevel(30)


class UserFilterTest(unittest.TestCase):
    def setUp(self):
        detail1 = testcommon.factory.create_user_detail(count_follows=11, count_followed_by=22, count_shared_media=33)
        self.user1 = instabotpatrik.model.InstagramUser(instagram_id="a", username="A", user_detail=detail1)


class UserShouldPassFollowsCountFilter(UserFilterTest):

    def runTest(self):
        follows_filter = instabotpatrik.filter.UserFollowsCountFilter(10, 15)
        self.assertTrue(follows_filter.passes(self.user1))


class UserShouldFailIsFollowsMoreThanRange(UserFilterTest):

    def runTest(self):
        follows_filter = instabotpatrik.filter.UserFollowsCountFilter(15, 20)
        self.assertFalse(follows_filter.passes(self.user1))


class UserShouldPassFollowedByCountFilter(UserFilterTest):

    def runTest(self):
        follows_filter = instabotpatrik.filter.UserFollowedByCountFilter(20, 25)
        # followed_by_filter = instabotpatrik.filter.UserFollowedByCountFilter(10, 1200)
        # follows_filter.
        self.assertTrue(follows_filter.passes(self.user1))


class UserShouldFailIsFollowedByMoreThanRange(UserFilterTest):

    def runTest(self):
        follows_filter = instabotpatrik.filter.UserFollowedByCountFilter(25, 30)
        self.assertFalse(follows_filter.passes(self.user1))


class UserShouldPassLikeTimestampAboveLimit(UserFilterTest):

    @unittest.mock.patch('time.time')
    def runTest(self, mock_time):
        like_filter = instabotpatrik.filter.LastLikeFilter(more_than_hours_ago=2)
        self.user1.bot_data = testcommon.factory.create_bot_data(
            last_like_timestamp=datetime.datetime(year=2012, month=10, day=1, hour=1).timestamp())
        mock_time.return_value = datetime.datetime(year=2012, month=10, day=1, hour=8).timestamp()
        self.assertTrue(like_filter.passes(self.user1))


class UserShouldNotPassLikeTimestampBelowLimit(UserFilterTest):

    @unittest.mock.patch('time.time')
    def runTest(self, mock_time):
        like_filter = instabotpatrik.filter.LastLikeFilter(more_than_hours_ago=2)
        self.user1.bot_data = testcommon.factory.create_bot_data(
            last_like_timestamp=datetime.datetime(year=2012, month=10, day=1, hour=1).timestamp())
        mock_time.return_value = datetime.datetime(year=2012, month=10, day=1, hour=2).timestamp()
        self.assertFalse(like_filter.passes(self.user1))


class UserShouldPassFollowTimestampAboveLimit(UserFilterTest):

    @unittest.mock.patch('time.time')
    def runTest(self, mock_time):
        follows_filter = instabotpatrik.filter.LastFollowFilter(more_than_hours_ago=2)
        self.user1.bot_data = testcommon.factory.create_bot_data(
            last_follow_timestamp=datetime.datetime(year=2012, month=10, day=1, hour=1).timestamp())
        mock_time.return_value = datetime.datetime(year=2012, month=10, day=1, hour=8).timestamp()
        self.assertTrue(follows_filter.passes(self.user1))


class UserShouldNotPassFollowTimestampBelowLimit(UserFilterTest):

    @unittest.mock.patch('time.time')
    def runTest(self, mock_time):
        follows_filter = instabotpatrik.filter.LastFollowFilter(more_than_hours_ago=2)
        self.user1.bot_data = testcommon.factory.create_bot_data(
            last_follow_timestamp=datetime.datetime(year=2012, month=10, day=1, hour=1).timestamp())
        mock_time.return_value = datetime.datetime(year=2012, month=10, day=1, hour=2).timestamp()
        self.assertFalse(follows_filter.passes(self.user1))


class UserShouldPassUnfollowTimestampAboveLimit(UserFilterTest):

    @unittest.mock.patch('time.time')
    def runTest(self, mock_time):
        unfollows_filter = instabotpatrik.filter.LastUnfollowFilter(more_than_hours_ago=2)
        self.user1.bot_data = testcommon.factory.create_bot_data(
            last_unfollow_timestamp=datetime.datetime(year=2012, month=10, day=1, hour=1).timestamp())
        mock_time.return_value = datetime.datetime(year=2012, month=10, day=1, hour=8).timestamp()
        self.assertTrue(unfollows_filter.passes(self.user1))


class UserShouldNotPassUnfollowTimestampBelowLimit(UserFilterTest):

    @unittest.mock.patch('time.time')
    def runTest(self, mock_time):
        unfollows_filter = instabotpatrik.filter.LastUnfollowFilter(more_than_hours_ago=2)
        self.user1.bot_data = testcommon.factory.create_bot_data(
            last_unfollow_timestamp=datetime.datetime(year=2012, month=10, day=1, hour=1).timestamp())
        mock_time.return_value = datetime.datetime(year=2012, month=10, day=1, hour=2).timestamp()
        self.assertFalse(unfollows_filter.passes(self.user1))
