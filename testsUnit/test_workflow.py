from testsUnit.context import instabotpatrik
from testsUnit.context import testcommon
import unittest.mock
import logging
import datetime
import freezegun
import pytz

logging.getLogger().setLevel(30)
logging.basicConfig(format='[%(levelname)s] [%(asctime)s] [%(name)s:%(funcName)s] : %(message)s',
                    datefmt='%m/%d/%Y-%H:%M:%S')


class ItShouldApproveUserForUnfollowIfUnkownFollowTimeAndHeDoesntFollowUs(unittest.TestCase):

    def runTest(self):
        detail = testcommon.factory.create_user_detail(user_follows_us=False, we_follow_user=True)
        history1 = instabotpatrik.model.InstagramUserBotData(
            last_follow_datetime=None)
        user1 = instabotpatrik.model.InstagramUser(instagram_id="a",
                                                   username="A",
                                                   user_detail=detail,
                                                   bot_data=history1)

        user_controller_mock = unittest.mock.create_autospec(instabotpatrik.core.UserController)
        user_controller_mock.get_fresh_user.return_value = user1
        unfollow_workflow = instabotpatrik.workflow.UnfollowWorkflow(user_controller=user_controller_mock)
        self.assertTrue(unfollow_workflow.is_approved_for_unfollow(user1))


class ItShouldNotApproveUserForUnfollowIfWeFollowedHimOnlyRecently(unittest.TestCase):

    @freezegun.freeze_time("2014-10-12 13:01:00", tz_offset=0)
    def runTest(self):
        detail = testcommon.factory.create_user_detail(user_follows_us=False,
                                                       we_follow_user=True)
        history1 = instabotpatrik.model.InstagramUserBotData(
            last_follow_datetime=datetime.datetime(year=2014, month=10, day=12, hour=13, minute=0, tzinfo=pytz.UTC))
        user1 = instabotpatrik.model.InstagramUser(instagram_id="a",
                                                   username="A",
                                                   user_detail=detail,
                                                   bot_data=history1)

        user_controller_mock = unittest.mock.create_autospec(instabotpatrik.core.UserController)
        user_controller_mock.get_fresh_user.return_value = user1
        unfollow_workflow = instabotpatrik.workflow.UnfollowWorkflow(user_controller=user_controller_mock)
        self.assertFalse(unfollow_workflow.is_approved_for_unfollow(user1))


class ItShouldNotApproveUserWeDontFollowAltoughtWeUsedToLongTimeAgo(unittest.TestCase):

    @freezegun.freeze_time("2014-10-12 13:01:00", tz_offset=0)
    def runTest(self):
        detail = testcommon.factory.create_user_detail(user_follows_us=False,
                                                       we_follow_user=False)
        history1 = instabotpatrik.model.InstagramUserBotData(
            last_follow_datetime=datetime.datetime(year=2014, month=9, day=1, hour=0, minute=0, tzinfo=pytz.UTC))
        user1 = instabotpatrik.model.InstagramUser(instagram_id="a",
                                                   username="A",
                                                   user_detail=detail,
                                                   bot_data=history1)

        user_controller_mock = unittest.mock.create_autospec(instabotpatrik.core.UserController)
        user_controller_mock.get_fresh_user.return_value = user1
        unfollow_workflow = instabotpatrik.workflow.UnfollowWorkflow(user_controller=user_controller_mock)
        self.assertFalse(unfollow_workflow.is_approved_for_unfollow(user1))


class ItShouldApproveUserForUnfollowIfWeFollowedHimLongTimeAgoButHeDoesntFollowsUs(unittest.TestCase):

    @freezegun.freeze_time("2014-10-12 13:01:00", tz_offset=0)
    def runTest(self):
        detail = testcommon.factory.create_user_detail(user_follows_us=False,
                                                       we_follow_user=True)
        history1 = instabotpatrik.model.InstagramUserBotData(
            last_follow_datetime=datetime.datetime(year=2014, month=9, day=1, hour=0, minute=0, tzinfo=pytz.UTC))
        user1 = instabotpatrik.model.InstagramUser(instagram_id="a",
                                                   username="A",
                                                   user_detail=detail,
                                                   bot_data=history1)

        user_controller_mock = unittest.mock.create_autospec(instabotpatrik.core.UserController)
        user_controller_mock.get_fresh_user.return_value = user1
        unfollow_workflow = instabotpatrik.workflow.UnfollowWorkflow(user_controller=user_controller_mock)
        self.assertTrue(unfollow_workflow.is_approved_for_unfollow(user1))
