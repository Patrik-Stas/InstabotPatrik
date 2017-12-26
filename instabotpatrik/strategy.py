import time
import random
import instabotpatrik
import logging


class StrategyMediaScanBasic:
    def __init__(self, media_controller): #
        """
        :type media_controller: instabotpatrik.core.MediaController
        """
        self.media_controller = media_controller

    def get_recent_media(self, tag):
        """
        Returns list of the most recently posted media, excluding our own.
        :param tag: tag to be scanner
        :return: list of recent media objects for tag
        :rtype: list of instabotpatrik.model.InstagramMedia
        """
        return self.media_controller.get_recent_media_by_tag(tag=tag, exclude=False)


class StrategyTagSelectionBasic:
    def __init__(self, get_candidate_tags):
        """
        :param get_candidate_tags: callable which returns list of strings (tags)
        :type get_candidate_tags: collections.abc.Callable
        """
        self.callable_get_tags = get_candidate_tags

    def get_tag(self):
        """
        Returns random tag from list to be scanned
        :rtype: string
        """
        tags = self.callable_get_tags()
        return random.choice(tags)
