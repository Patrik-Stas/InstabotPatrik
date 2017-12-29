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
        self.detail1 = testcommon.factory.create_user_detail(count_follows=11, count_followed_by=22,
                                                             count_shared_media=33,
                                                             user_follows_us=True)
        self.history1 = instabotpatrik.model.InstagramUserBotData(
            last_like_datetime=datetime.datetime(year=2012, month=10, day=10, hour=10, tzinfo=pytz.UTC),
            last_follow_datetime=datetime.datetime(year=2014, month=10, day=10, hour=10, tzinfo=pytz.UTC),
            last_unfollow_datetime=datetime.datetime(year=2016, month=10, day=10, hour=10, tzinfo=pytz.UTC))
        self.user1 = instabotpatrik.model.InstagramUser(instagram_id="a",
                                                        username="A",
                                                        user_detail=self.detail1,
                                                        bot_data=self.history1)


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

    @freezegun.freeze_time("2012-10-10 13:00:00", tz_offset=0)
    def runTest(self):
        like_filter = instabotpatrik.filter.LastLikeFilter(more_than_hours_ago=2)
        self.assertTrue(like_filter.passes(self.user1))


class UserShouldNotPassLikeTimestampBelowLimit(UserFilterTest):

    @freezegun.freeze_time("2012-10-10 13:00:00", tz_offset=0)
    def runTest(self):
        like_filter = instabotpatrik.filter.LastLikeFilter(more_than_hours_ago=4)
        self.assertFalse(like_filter.passes(self.user1))


class UserShouldPassFollowTimestampAboveLimit(UserFilterTest):

    @freezegun.freeze_time("2014-10-10 13:00:00", tz_offset=0)
    def runTest(self):
        follows_filter = instabotpatrik.filter.LastFollowFilter(more_than_hours_ago=2)
        self.assertTrue(follows_filter.passes(self.user1))


class UserShouldNotPassFollowTimestampBelowLimit(UserFilterTest):

    @freezegun.freeze_time("2014-10-10 13:00:00", tz_offset=0)
    def runTest(self):
        follows_filter = instabotpatrik.filter.LastFollowFilter(more_than_hours_ago=4)
        self.assertFalse(follows_filter.passes(self.user1))


class UserShouldPassUnfollowTimestampAboveLimit(UserFilterTest):

    @freezegun.freeze_time("2016-10-10 13:00:00", tz_offset=0)
    def runTest(self):
        unfollows_filter = instabotpatrik.filter.LastUnfollowFilter(more_than_hours_ago=2)
        self.assertTrue(unfollows_filter.passes(self.user1))


class UserShouldNotPassUnfollowTimestampBelowLimit(UserFilterTest):

    @freezegun.freeze_time("2016-10-10 13:00:00", tz_offset=0)
    def runTest(self):
        unfollows_filter = instabotpatrik.filter.LastUnfollowFilter(more_than_hours_ago=4)
        self.assertFalse(unfollows_filter.passes(self.user1))


class ItShouldNotPassIfUserIsFollowingUs(UserFilterTest):

    def runTest(self):
        follows_us_filter = instabotpatrik.filter.UserIsNotFollowingUs()
        self.assertFalse(follows_us_filter.passes(self.user1))


class ItShouldPassIfUserIsNotFollowingUs(UserFilterTest):

    def runTest(self):
        detail2 = testcommon.factory.create_user_detail(count_follows=11, count_followed_by=22, count_shared_media=33,
                                                        user_follows_us=False)
        user_not_following_us = instabotpatrik.model.InstagramUser(instagram_id="a",
                                                                   username="A",
                                                                   user_detail=detail2)
        follows_us_filter = instabotpatrik.filter.UserIsNotFollowingUs()
        self.assertTrue(follows_us_filter.passes(user_not_following_us))
