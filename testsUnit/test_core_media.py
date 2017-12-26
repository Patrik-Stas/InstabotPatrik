# -*- coding: utf-8 -*-

import unittest
import unittest.mock

from testsUnit.context import instabotpatrik


class MediaControllerTestCase(unittest.TestCase):
    def setUp(self):
        self.client_mock = unittest.mock.create_autospec(instabotpatrik.client.InstagramClient)
        self.repo_mock = unittest.mock.create_autospec(instabotpatrik.repository.BotRepositoryMongoDb)
        self.media_controller = instabotpatrik.core.MediaController(repository=self.repo_mock,
                                                                    api_client=self.client_mock)


class ItShouldReturnAllMediaWihoutExcludes(MediaControllerTestCase):

    def test_run(self):
        media = [instabotpatrik.model.InstagramMedia("id1", "code1", "owner_id1", "caption1"),
                 instabotpatrik.model.InstagramMedia("id2", "code2", "my_id", "caption2")]
        self.client_mock.get_recent_media_by_tag.return_value = media
        foobar_medias = self.media_controller.get_recent_media_by_tag("whatever")
        self.assertEqual(2, len(foobar_medias))
        self.assertTrue("code1" in [media.shortcode for media in foobar_medias])
        self.assertTrue("code2" in [media.shortcode for media in foobar_medias])


class ItShouldExcludeMediaByOwnerUsername(MediaControllerTestCase):

    def test_run(self):
        media = [instabotpatrik.model.InstagramMedia("id1", "code1", "owner_id1", "caption1", owner_username="username"),
                 instabotpatrik.model.InstagramMedia("id2", "code2", "my_id", "caption2", owner_username="my_username")]
        self.client_mock.get_recent_media_by_tag.return_value = media
        foobar_medias = self.media_controller.get_recent_media_by_tag("whatever", excluded_owner_usernames=["my_username"])
        self.assertEqual(1, len(foobar_medias))
        self.assertTrue("code1" in [media.shortcode for media in foobar_medias])

#
# class ItShouldUpdateLikeTimestampForUserWhenLikeIsGiven(MediaControllerTestCase):
#     def test_run(self):
#         media = [instabotpatrik.model.InstagramMedia("id1", "code1", "owner_id1", "caption1"),
#                  instabotpatrik.model.InstagramMedia("id2", "code2", "my_id", "caption2")]
#
#
# class ItShouldNotOverwriteIrrelevantValuesOnUserWhenLikeIsGiven(MediaControllerTestCase):
#     def test_run(self):
#         media = [instabotpatrik.model.InstagramMedia("id1", "code1", "owner_id1", "caption1"),
#                  instabotpatrik.model.InstagramMedia("id2", "code2", "my_id", "caption2")]
#

class ItShouldThrowInstabotExceptionIfGivingLikeWasNotSuccess(MediaControllerTestCase):
    def test_run(self):
        media = [instabotpatrik.model.InstagramMedia("id1", "code1", "owner_id1", "caption1"),
                 instabotpatrik.model.InstagramMedia("id2", "code2", "my_id", "caption2")]


class ItShouldThrowInstabotExceptionIfGivingLikeFailed(MediaControllerTestCase):
    def test_run(self):
        media = [instabotpatrik.model.InstagramMedia("id1", "code1", "owner_id1", "caption1"),
                 instabotpatrik.model.InstagramMedia("id2", "code2", "my_id", "caption2")]


class ItShouldNotCallLikeApiIfMediaWasAlreadyLiked(MediaControllerTestCase):
    def test_run(self):
        media = [instabotpatrik.model.InstagramMedia("id1", "code1", "owner_id1", "caption1"),
                 instabotpatrik.model.InstagramMedia("id2", "code2", "my_id", "caption2")]


class ItShouldReturnRecentMediaOfUser(MediaControllerTestCase):
    def test_run(self):
        media = [instabotpatrik.model.InstagramMedia("id1", "code1", "owner_id1", "caption1"),
                 instabotpatrik.model.InstagramMedia("id2", "code2", "my_id", "caption2")]
