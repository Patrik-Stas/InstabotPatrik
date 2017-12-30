# -*- coding: utf-8 -*-
import logging
import unittest
import unittest.mock

import requests
import requests.models

import testsUnit.data_action_responses
import testsUnit.data_get_media_by_tag
import testsUnit.data_get_media_detail
import testsUnit.data_get_user_detail
from testsUnit.context import instabotpatrik

logging.getLogger().setLevel(30)
logging.basicConfig(format='[%(levelname)s] [%(asctime)s] [%(name)s:%(funcName)s] : %(message)s',
                    datefmt='%m/%d/%Y-%H:%M:%S')


class ItShouldParseGetMediaByTag(unittest.TestCase):

    @unittest.mock.patch('time.sleep')
    def test_run(self, mock_sleep):
        session_mock = unittest.mock.create_autospec(requests.Session)
        resp_mock = unittest.mock.Mock(status_code=200, text=testsUnit.data_get_media_by_tag.response)
        session_mock.get.return_value = resp_mock
        client = instabotpatrik.client.InstagramClient(
            user_login="abcd",
            user_password="xyz",
            requests_session=session_mock
        )

        medias = client.get_recent_media_by_tag("prague")

        first = medias[0]
        self.assertEqual(len(medias), 17, "No media received")
        self.assertEqual(first.instagram_id, "1661696503407488208")
        self.assertEqual(first.owner_id, "5550257784")
        self.assertEqual(first.shortcode, "BcPiCpyHKzQ")
        session_mock.get.assert_called_with("https://www.instagram.com/explore/tags/prague/?__a=1")


class ItShouldParseMediaDetail(unittest.TestCase):

    @unittest.mock.patch('time.sleep')
    def test_run(self, mock_sleep):
        session_mock = unittest.mock.create_autospec(requests.Session)
        resp_mock = unittest.mock.Mock(status_code=200, text=testsUnit.data_get_media_detail.response)
        session_mock.get.return_value = resp_mock
        client = instabotpatrik.client.InstagramClient(
            user_login="abcd",
            user_password="xyz",
            requests_session=session_mock
        )

        media = client.get_media_detail("mediaCodeABCDE")

        self.assertEqual(media.instagram_id, "1640908281679491991")
        self.assertEqual(media.shortcode, "BbFrWNmgLOX")
        self.assertEqual(media.owner_id, "5804069718")
        self.assertEqual(media.caption, "프라하 안에서는 웬만해서는 #차로")
        self.assertEqual(media.is_liked, True)
        self.assertEqual(media.like_count, 294)
        self.assertEqual(media.time_liked, None)
        self.assertEqual(media.owner_username, "ownername")
        session_mock.get.assert_called_with("https://www.instagram.com/p/mediaCodeABCDE/?__a=1")


class GetMediaDetailShouldThrowMediaNotFoundExceptionIfResponseCodeIs404(unittest.TestCase):

    @unittest.mock.patch('time.sleep')
    def test_run(self, mock_sleep):
        session_mock = unittest.mock.create_autospec(requests.Session)
        resp_mock = unittest.mock.Mock(status_code=404, text=testsUnit.data_get_media_detail.response)
        session_mock.get.return_value = resp_mock
        client = instabotpatrik.client.InstagramClient(
            user_login="abcd",
            user_password="xyz",
            requests_session=session_mock
        )

        with self.assertRaises(instabotpatrik.client.MediaNotFoundException) as cm:
            client.get_media_detail("someshortcode_ABC")
        the_exception = cm.exception
        self.assertEqual(the_exception.shortcode, "someshortcode_ABC")


class GetMediaDetailShouldRaiseBottingDetectedExceptionIfResponseCodeIs404(unittest.TestCase):

    @unittest.mock.patch('time.sleep')
    def test_run(self, mock_sleep):
        session_mock = unittest.mock.create_autospec(requests.Session)
        resp_mock = unittest.mock.Mock(status_code=400, text="Doesnt matter in case of 400")
        session_mock.get.return_value = resp_mock
        client = instabotpatrik.client.InstagramClient(
            user_login="abcd",
            user_password="xyz",
            requests_session=session_mock
        )

        self.assertRaises(instabotpatrik.client.BottingDetectedException, client.get_media_detail,
                          "someshortcode_ABC")


class ItShouldParseUserDetails(unittest.TestCase):

    @unittest.mock.patch('time.sleep')
    def test_run(self, mock_sleep):
        session_mock = unittest.mock.create_autospec(requests.Session)
        resp_mock = unittest.mock.Mock(status_code=200, text=testsUnit.data_get_user_detail.response)
        session_mock.get.return_value = resp_mock
        client = instabotpatrik.client.InstagramClient(
            user_login="abcd",
            user_password="xyz",
            requests_session=session_mock
        )

        user = client.get_user_with_details("traveluser")

        self.assertEqual(user.instagram_id, "5804069718")
        self.assertEqual(user.username, "traveltravel")
        self.assertEqual(user.url, "http://www.user-url.com/")
        self.assertEqual(user.count_shared_media, 70)
        self.assertEqual(user.count_follows, 3873)
        self.assertEqual(user.count_followed_by, 2198)
        self.assertEqual(user.we_follow_user, False)
        self.assertEqual(user.user_follows_us, True)
        session_mock.get.assert_called_with("https://www.instagram.com/traveluser/?__a=1")


class GetRecentMediaOfUserShouldRaiseUserNotFoundExceptionOn404(unittest.TestCase):

    @unittest.mock.patch('time.sleep')
    def test_run(self, mock_sleep):
        session_mock = unittest.mock.create_autospec(requests.Session)
        resp_mock = unittest.mock.Mock(status_code=404, text="This should not matter in case of 404")
        session_mock.get.return_value = resp_mock
        client = instabotpatrik.client.InstagramClient(
            user_login="abcd",
            user_password="xyz",
            requests_session=session_mock
        )
        with self.assertRaises(instabotpatrik.client.UserNotFoundException) as cm:
            client.get_recent_media_of_user("someusername")
        the_exception = cm.exception
        self.assertEqual(the_exception.username, "someusername")


class GetRecentMediaOfUserShouldRaiseBottingDetectedOnCode400(unittest.TestCase):

    @unittest.mock.patch('time.sleep')
    def test_run(self, mock_sleep):
        session_mock = unittest.mock.create_autospec(requests.Session)
        resp_mock = unittest.mock.Mock(status_code=400, text="This should not matter in case of 404")
        session_mock.get.return_value = resp_mock
        client = instabotpatrik.client.InstagramClient(
            user_login="abcd",
            user_password="xyz",
            requests_session=session_mock
        )
        with self.assertRaises(instabotpatrik.client.BottingDetectedException) as cm:
            client.get_recent_media_of_user("someusername")


class GetUserShouldRaiseUserNotFoundExceptionOn404(unittest.TestCase):

    @unittest.mock.patch('time.sleep')
    def test_run(self, mock_sleep):
        session_mock = unittest.mock.create_autospec(requests.Session)
        resp_mock = unittest.mock.Mock(status_code=404, text="This should not matter in case of 404")
        session_mock.get.return_value = resp_mock
        client = instabotpatrik.client.InstagramClient(
            user_login="abcd",
            user_password="xyz",
            requests_session=session_mock
        )

        with self.assertRaises(instabotpatrik.client.UserNotFoundException) as cm:
            client.get_user_with_details("someusername")
        the_exception = cm.exception
        self.assertEqual(the_exception.username, "someusername")


class GetUserShouldRaiseBottingDetectedExceptionOn400(unittest.TestCase):

    @unittest.mock.patch('time.sleep')
    def test_run(self, mock_sleep):
        session_mock = unittest.mock.create_autospec(requests.Session)
        resp_mock = unittest.mock.Mock(status_code=400, text="Might not be json on 400")
        session_mock.get.return_value = resp_mock
        client = instabotpatrik.client.InstagramClient(
            user_login="abcd",
            user_password="xyz",
            requests_session=session_mock
        )

        with self.assertRaises(instabotpatrik.client.BottingDetectedException) as cm:
            client.get_user_with_details("someusername")


class ItShouldLikePost(unittest.TestCase):
    @unittest.mock.patch('time.sleep')
    def test_run(self, mock_sleep):
        session_mock = unittest.mock.create_autospec(requests.Session)
        resp_mock = unittest.mock.Mock(status_code=200, text=testsUnit.data_action_responses.response_like)
        session_mock.post.return_value = resp_mock
        client = instabotpatrik.client.InstagramClient(
            user_login="abcd",
            user_password="xyz",
            requests_session=session_mock
        )

        client.like("mediaid_12312")
        session_mock.post.assert_called_with("https://www.instagram.com/web/likes/mediaid_12312/like/")


class LikeShouldRaiseBottingDetectedExceptionOn401(unittest.TestCase):
    @unittest.mock.patch('time.sleep')
    def test_run(self, mock_sleep):
        session_mock = unittest.mock.create_autospec(requests.Session)
        resp_mock = unittest.mock.Mock(status_code=401, text=testsUnit.data_action_responses.response_like)
        session_mock.post.return_value = resp_mock
        client = instabotpatrik.client.InstagramClient(
            user_login="abcd",
            user_password="xyz",
            requests_session=session_mock
        )

        with self.assertRaises(instabotpatrik.client.BottingDetectedException) as cm:
            client.like("media_id")


class LikeShouldRaiseInstagramResponseException(unittest.TestCase):
    @unittest.mock.patch('time.sleep')
    def test_run(self, mock_sleep):
        session_mock = unittest.mock.create_autospec(requests.Session)
        resp_mock = unittest.mock.Mock(status_code=200, text='{"status": "error"}')
        session_mock.post.return_value = resp_mock
        client = instabotpatrik.client.InstagramClient(
            user_login="abcd",
            user_password="xyz",
            requests_session=session_mock
        )

        with self.assertRaises(instabotpatrik.client.InstagramResponseException) as cm:
            client.like("media_id")


class ItShouldFollowUser(unittest.TestCase):
    @unittest.mock.patch('time.sleep')
    def test_run(self, mock_sleep):
        session_mock = unittest.mock.create_autospec(requests.Session)
        resp_mock = unittest.mock.Mock(status_code=200, text=testsUnit.data_action_responses.response_follow)
        session_mock.post.return_value = resp_mock
        client = instabotpatrik.client.InstagramClient(
            user_login="abcd",
            user_password="xyz",
            requests_session=session_mock
        )

        client.follow("someuser_id")
        session_mock.post.assert_called_with("https://www.instagram.com/web/friendships/someuser_id/follow/")


class FollowShouldRaiseInstagramResponseException(unittest.TestCase):
    @unittest.mock.patch('time.sleep')
    def test_run(self, mock_sleep):
        session_mock = unittest.mock.create_autospec(requests.Session)
        resp_mock = unittest.mock.Mock(status_code=200, text='{"status": "error"}')
        session_mock.post.return_value = resp_mock
        client = instabotpatrik.client.InstagramClient(
            user_login="abcd",
            user_password="xyz",
            requests_session=session_mock
        )

        with self.assertRaises(instabotpatrik.client.InstagramResponseException) as cm:
            client.follow("user_id")


class ItShouldUnfollowUser(unittest.TestCase):
    @unittest.mock.patch('time.sleep')
    def test_run(self, mock_sleep):
        session_mock = unittest.mock.create_autospec(requests.Session)
        resp_mock = unittest.mock.Mock(status_code=200, text=testsUnit.data_action_responses.response_unfollow)
        session_mock.post.return_value = resp_mock
        client = instabotpatrik.client.InstagramClient(
            user_login="abcd",
            user_password="xyz",
            requests_session=session_mock
        )

        client.unfollow("someuser_id")
        session_mock.post.assert_called_with("https://www.instagram.com/web/friendships/someuser_id/unfollow/")


class FollowShouldRaiseInstagramResponseException(unittest.TestCase):
    @unittest.mock.patch('time.sleep')
    def test_run(self, mock_sleep):
        session_mock = unittest.mock.create_autospec(requests.Session)
        resp_mock = unittest.mock.Mock(status_code=200, text='{"status": "error"}')
        session_mock.post.return_value = resp_mock
        client = instabotpatrik.client.InstagramClient(
            user_login="abcd",
            user_password="xyz",
            requests_session=session_mock
        )

        with self.assertRaises(instabotpatrik.client.InstagramResponseException) as cm:
            client.unfollow("user_id")


if __name__ == '__main__':
    unittest.main()
