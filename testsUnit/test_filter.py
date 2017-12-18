from testsUnit.context import instabotpatrik
from testsUnit.context import testcommon
import unittest.mock
import logging
import datetime
import freezegun
import pytz

logging.getLogger().setLevel(30)


class UserFilterTest(unittest.TestCase):
    def setUp(self):
        detail1 = testcommon.factory.create_user_detail(count_follows=11, count_followed_by=22, count_shared_media=33)
        history1 = testcommon.factory.create_bot_data(
            dt_like=datetime.datetime(year=2012, month=10, day=10, hour=10, tzinfo=pytz.UTC),
            dt_follow=datetime.datetime(year=2014, month=10, day=10, hour=10, tzinfo=pytz.UTC),
            dt_unfollow=datetime.datetime(year=2016, month=10, day=10, hour=10, tzinfo=pytz.UTC))
        self.user1 = instabotpatrik.model.InstagramUser(instagram_id="a",
                                                        username="A",
                                                        user_detail=detail1,
                                                        bot_history=history1)


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

    @freezegun.freeze_time("2012-10-12 13:00:00", tz_offset=0)
    def runTest(self):
        like_filter = instabotpatrik.filter.LastLikeFilter(more_than_hours_ago=2)
        self.assertTrue(like_filter.passes(self.user1))


class UserShouldNotPassLikeTimestampBelowLimit(UserFilterTest):

    @freezegun.freeze_time("2012-10-12 13:00:00", tz_offset=0)
    def runTest(self):
        like_filter = instabotpatrik.filter.LastLikeFilter(more_than_hours_ago=4)
        self.assertFalse(like_filter.passes(self.user1))


class UserShouldPassFollowTimestampAboveLimit(UserFilterTest):

    @freezegun.freeze_time("2014-10-12 13:00:00", tz_offset=0)
    def runTest(self):
        follows_filter = instabotpatrik.filter.LastFollowFilter(more_than_hours_ago=2)
        self.assertTrue(follows_filter.passes(self.user1))


class UserShouldNotPassFollowTimestampBelowLimit(UserFilterTest):

    @freezegun.freeze_time("2014-10-12 13:00:00", tz_offset=0)
    def runTest(self):
        follows_filter = instabotpatrik.filter.LastFollowFilter(more_than_hours_ago=4)
        self.assertFalse(follows_filter.passes(self.user1))


class UserShouldPassUnfollowTimestampAboveLimit(UserFilterTest):

    @freezegun.freeze_time("2016-10-12 13:00:00", tz_offset=0)
    def runTest(self):
        unfollows_filter = instabotpatrik.filter.LastUnfollowFilter(more_than_hours_ago=2)
        self.assertTrue(unfollows_filter.passes(self.user1))


class UserShouldNotPassUnfollowTimestampBelowLimit(UserFilterTest):

    @freezegun.freeze_time("2016-10-12 13:00:00", tz_offset=0)
    def runTest(self):
        unfollows_filter = instabotpatrik.filter.LastUnfollowFilter(more_than_hours_ago=4)
        self.assertFalse(unfollows_filter.passes(self.user1))
