# -*- coding: utf-8 -*-
from testsIntegrationAPI.context import instabotpatrik
import unittest
import requests
import yaml
import os


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

    def runTest(self):
        credentials = self.load_instagram_credentials()
        self.client = instabotpatrik.client.InstagramClient(
            user_login=credentials['user']['username'],
            user_password=credentials['user']['password'],
            requests_session=requests.Session()
        )
        medias = self.client.get_latest_media_by_tag("prague")
        first = medias[0]
        self.assertGreater(len(medias), 0, "No media received")
        self.assertIsNotNone(first.instagram_id)
        self.assertIsNotNone(first.owner_id)
        self.assertIsNotNone(first.shortcode)
        print(str(medias[0]))

    def tearDown(self):
        self.client.logout()


if __name__ == '__main__':
    unittest.main()
