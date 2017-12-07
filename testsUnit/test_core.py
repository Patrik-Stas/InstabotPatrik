# -*- coding: utf-8 -*-

from testsUnit.context import instabotpatrik
from unittest.mock import patch
import unittest
import unittest.mock


class ItShouldNotIncludeOwnMediaByDefault(unittest.TestCase):
    def setUp(self):
        self.client_mock = unittest.mock.create_autospec(instabotpatrik.client.InstagramClient)
        self.repo_mock = unittest.mock.create_autospec(instabotpatrik.repository.BotRepositoryMongoDb)
        self.core = instabotpatrik.core.InstabotCore(repository=self.repo_mock, api_client=self.client_mock)

    def test_run(self):
        media = [instabotpatrik.model.InstagramMedia("id1", "code1", "owner_id1", "caption1"),
                 instabotpatrik.model.InstagramMedia("id2", "code2", "my_id", "caption2")]
        self.client_mock.get_latest_media_by_tag.return_value = media
        self.client_mock.our_instagram_id = "my_id"
        foobar_medias = self.core.get_latest_media_by_tag("foobar")
        self.assertEqual(1, len(foobar_medias))
        self.assertEqual("owner_id1", foobar_medias[0].owner_id)
