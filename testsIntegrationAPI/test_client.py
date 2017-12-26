# -*- coding: utf-8 -*-
from testsIntegrationAPI.context import instabotpatrik
import unittest
import requests
import yaml
import time
import os
import logging
import freezegun
import pytz
import datetime

logging.getLogger().setLevel(20)


class ItShouldLoginAndGetMedia(unittest.TestCase):
    @staticmethod
    def get_path_to_file_in_directory_of_this_file(file_name):
        this_directory_absolute = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        return os.path.join(this_directory_absolute, file_name)

    def load_instagram_credentials(self):
        with open(self.get_path_to_file_in_directory_of_this_file("credentials.secret.yaml"), 'r') as stream:
            try:
                return yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)

    @freezegun.freeze_time("2011-11-11 11:00:00", tz_offset=0)
    def runTest(self):
        credentials = self.load_instagram_credentials()
        self.client = instabotpatrik.client.InstagramClient(
            user_login=credentials['user']['username'],
            user_password=credentials['user']['password'],
            requests_session=requests.Session(),
            try_to_load_session_from_file=True
        )
        self.client.login()
        self.assertEqual(credentials['user']['username'], self.client.get_our_user().username)

        my_recent = self.client.get_recent_media_of_user(username=self.client.get_our_user().username)
        self.assertGreaterEqual(len(my_recent), 2)
        my_last_media = my_recent[0]
        self.assertIsNone(my_last_media.is_liked)  # as of instagram right now, this is not included in the response
        self.assertIsNone(my_last_media.time_liked)  # bot history, not known by instagram
        self.assertIsNotNone(my_last_media.instagram_id)
        self.assertIsNotNone(my_last_media.owner_username)
        self.assertIsNotNone(my_last_media.shortcode)
        self.assertEqual(my_last_media.owner_username, self.client.get_our_user().username)
        self.assertEqual(my_last_media.owner_id, self.client.get_our_user().instagram_id)

        time.sleep(5)

        my_media_before_like = self.client.get_media_detail(my_last_media.shortcode)
        self.assertIsNotNone(my_media_before_like.is_liked)
        self.assertIsNone(my_media_before_like.time_liked)  # bot history, not known on client level, filled by core
        self.assertEqual(my_last_media.shortcode, my_media_before_like.shortcode)
        self.assertEqual(my_last_media.owner_username, my_media_before_like.owner_username)
        self.assertEqual(my_last_media.owner_id, my_media_before_like.owner_id)
        self.assertEqual(my_last_media.instagram_id, my_media_before_like.instagram_id)
        self.assertEqual(my_last_media.caption, my_media_before_like.caption)

        time.sleep(5)

        like_self_success = self.client.like(media_id=my_last_media.instagram_id)
        self.assertTrue(like_self_success)

        time.sleep(5)

        my_media_after_like = self.client.get_media_detail(my_last_media.shortcode)
        self.assertTrue(my_media_before_like.is_liked)
        self.assertEqual(my_last_media.shortcode, my_media_after_like.shortcode)
        self.assertEqual(my_last_media.owner_username, my_media_after_like.owner_username)
        self.assertEqual(my_last_media.owner_id, my_media_after_like.owner_id)
        self.assertEqual(my_last_media.instagram_id, my_media_after_like.instagram_id)
        self.assertEqual(my_last_media.caption, my_media_after_like.caption)
        time.sleep(5)

        medias = self.client.get_recent_media_by_tag("chickensteak")
        self.assertGreater(len(medias), 0, "No media received")

        first = medias[0]
        self.assertIsNotNone(first.instagram_id)
        self.assertIsNotNone(first.owner_id)
        self.assertIsNotNone(first.shortcode)

        logging.info("Liking first media with shortcode %s", first.shortcode)
        logging.info("Liking first media by owner id: %s", first.instagram_id)
        like_success1 = self.client.like(first.instagram_id)

        self.assertTrue(like_success1)
        time.sleep(10)

        second = medias[1]
        logging.info("Liking second media with shortcode %s", second.shortcode)
        logging.info("Liking second media by owner username: %s", second.instagram_id)
        like_success2 = self.client.like(second.instagram_id)
        self.assertTrue(like_success2)


if __name__ == '__main__':
    unittest.main()
