# -*- coding: utf-8 -*-
from testsUnit.context import instabotpatrik
from unittest.mock import patch
import unittest
import unittest.mock
import requests
import requests.models
import testsUnit.data_get_media_by_tag
import testsUnit.data_action_responses
import testsUnit.data_get_media_detail
import testsUnit.data_get_user_detail
import logging

logging.getLogger().setLevel(30)


class ItShouldParseGetMediaByTag(unittest.TestCase):
    def test_run(self):
        session_mock = unittest.mock.create_autospec(requests.Session)
        resp_mock = unittest.mock.Mock(status_code=200, text=testsUnit.data_get_media_by_tag.response)
        session_mock.get.return_value = resp_mock
        client = instabotpatrik.client.InstagramClient(
            user_login="abcd",
            user_password="xyz",
            requests_session=session_mock
        )

        medias = client.get_media_by_tag("prague")

        first = medias[0]
        self.assertEqual(len(medias), 17, "No media received")
        self.assertEqual(first.id, "1661696503407488208")
        self.assertEqual(first.owner_id, "5550257784")
        self.assertEqual(first.shortcode, "BcPiCpyHKzQ")
        session_mock.get.assert_called_with("https://www.instagram.com/explore/tags/prague/?__a=1")


class ItShouldParseMediaDetail(unittest.TestCase):
    def test_run(self):
        session_mock = unittest.mock.create_autospec(requests.Session)
        resp_mock = unittest.mock.Mock(status_code=200, text=testsUnit.data_get_media_detail.response)
        session_mock.get.return_value = resp_mock
        client = instabotpatrik.client.InstagramClient(
            user_login="abcd",
            user_password="xyz",
            requests_session=session_mock
        )

        media = client.get_media_detail("mediaCodeABCDE")

        self.assertEqual(media.id, "1640908281679491991")
        self.assertEqual(media.shortcode, "BbFrWNmgLOX")
        self.assertEqual(media.owner_id, "5804069718")
        self.assertEqual(media.caption, "프라하 안에서는 웬만해서는 #차로")
        self.assertEqual(media.is_liked, True)
        self.assertEqual(media.like_count, 294)
        self.assertEqual(media.time_liked, None)
        self.assertEqual(media.owner_username, "ownername")
        session_mock.get.assert_called_with("https://www.instagram.com/p/mediaCodeABCDE/?__a=1")


class ItShouldParseUserDetails(unittest.TestCase):
    def test_run(self):
        session_mock = unittest.mock.create_autospec(requests.Session)
        resp_mock = unittest.mock.Mock(status_code=200, text=testsUnit.data_get_user_detail.response)
        session_mock.get.return_value = resp_mock
        client = instabotpatrik.client.InstagramClient(
            user_login="abcd",
            user_password="xyz",
            requests_session=session_mock
        )

        user = client.get_user_detail("traveluser")

        self.assertEqual(user.id, "5804069718")
        self.assertEqual(user.username, "traveltravel")
        self.assertEqual(user.url, "http://www.user-url.com/")
        self.assertEqual(user.count_shared_media, 70)
        self.assertEqual(user.count_follows, 3873)
        self.assertEqual(user.count_followed_by, 2198)
        self.assertEqual(user.we_follow_user, False)
        self.assertEqual(user.user_follows_us, True)
        session_mock.get.assert_called_with("https://www.instagram.com/traveluser/?__a=1")


class ItShouldLikePost(unittest.TestCase):
    def test_run(self):
        session_mock = unittest.mock.create_autospec(requests.Session)
        resp_mock = unittest.mock.Mock(status_code=200, text=testsUnit.data_action_responses.response_like)
        session_mock.post.return_value = resp_mock
        client = instabotpatrik.client.InstagramClient(
            user_login="abcd",
            user_password="xyz",
            requests_session=session_mock
        )

        success = client.like("mediaid_12312")
        self.assertTrue(success)
        session_mock.post.assert_called_with("https://www.instagram.com/web/likes/mediaid_12312/like/")


class ItShouldFollowUser(unittest.TestCase):
    def test_run(self):
        session_mock = unittest.mock.create_autospec(requests.Session)
        resp_mock = unittest.mock.Mock(status_code=200, text=testsUnit.data_action_responses.response_follow)
        session_mock.post.return_value = resp_mock
        client = instabotpatrik.client.InstagramClient(
            user_login="abcd",
            user_password="xyz",
            requests_session=session_mock
        )

        success = client.follow("someuser_id")
        self.assertTrue(success)
        session_mock.post.assert_called_with("https://www.instagram.com/web/friendships/someuser_id/follow/")


class ItShouldUnfollowUser(unittest.TestCase):
    def test_run(self):
        session_mock = unittest.mock.create_autospec(requests.Session)
        resp_mock = unittest.mock.Mock(status_code=200, text=testsUnit.data_action_responses.response_unfollow)
        session_mock.post.return_value = resp_mock
        client = instabotpatrik.client.InstagramClient(
            user_login="abcd",
            user_password="xyz",
            requests_session=session_mock
        )

        success = client.unfollow("someuser_id")
        self.assertTrue(success)
        session_mock.post.assert_called_with("https://www.instagram.com/web/friendships/someuser_id/unfollow/")


if __name__ == '__main__':
    unittest.main()
