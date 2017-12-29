# -*- coding: utf-8 -*-

import unittest
import unittest.mock
from unittest.mock import patch

from testsUnit.context import instabotpatrik
from testsUnit.context import testcommon
import logging

logging.getLogger().setLevel(30)
logging.basicConfig(format='[%(levelname)s] [%(asctime)s] [%(name)s:%(funcName)s] : %(message)s',
                    datefmt='%m/%d/%Y-%H:%M:%S')


class UserControllerTestCase(unittest.TestCase):
    def setUp(self):
        self.client_mock = unittest.mock.create_autospec(instabotpatrik.client.InstagramClient)
        self.repo_mock = unittest.mock.create_autospec(instabotpatrik.repository.BotRepositoryMongoDb)
        self.user_controller = instabotpatrik.core.UserController(repository=self.repo_mock,
                                                                  api_client=self.client_mock)


# FOLLOW
class ItShouldNotUseApiClientIfWeAlreadyFollowUser(UserControllerTestCase):
    def test_run(self):
        self.user_detail = testcommon.factory.create_user_detail(we_follow_user=True)
        user = instabotpatrik.model.InstagramUser("user1", "username1", user_detail=self.user_detail)
        self.repo_mock.find_user.return_value = user

        self.user_controller.follow(user.instagram_id)

        self.client_mock.follow.assert_not_called()


class ItShouldThrowInstabotExceptionIfClientFollowIsNotSuccess(UserControllerTestCase):
    def test_run(self):
        self.user_detail = testcommon.factory.create_user_detail(we_follow_user=False)
        user = instabotpatrik.model.InstagramUser("user1", "username1", user_detail=self.user_detail)
        self.repo_mock.find_user.return_value = user
        self.client_mock.follow.return_value = False

        self.assertRaises(instabotpatrik.core.InstabotException, self.user_controller.follow, user.instagram_id)


# UNFOLLOW

class ItShouldNotUseApiClientOnUnfollowIfWeAreNotFollowingUser(UserControllerTestCase):
    def test_run(self):
        self.user_detail = testcommon.factory.create_user_detail(we_follow_user=False)
        user = instabotpatrik.model.InstagramUser("user1", "username1", user_detail=self.user_detail)
        self.repo_mock.find_user.return_value = user

        self.user_controller.unfollow(user.instagram_id)

        self.client_mock.unfollow.assert_not_called()


class ItShouldThrowInstabotExceptionIfClientUnfollowIsNotSuccess(UserControllerTestCase):
    def test_run(self):
        self.user_detail = testcommon.factory.create_user_detail(we_follow_user=True)
        user = instabotpatrik.model.InstagramUser("user1", "username1", user_detail=self.user_detail)
        self.repo_mock.find_user.return_value = user
        self.client_mock.unfollow.return_value = False

        self.assertRaises(instabotpatrik.core.InstabotException, self.user_controller.unfollow, user.instagram_id)
