import time
import random
import instabotpatrik
import logging

logging.getLogger().setLevel(20)  # INFO+
logging.basicConfig(format='[%(levelname)s] [%(asctime)s] %(message)s', datefmt='%m/%d/%Y-%H:%M:%S')


class StrategyMediaScanBasic:
    def __init__(self, core):
        """
        :type core: instabotpatrik.core.InstabotCore
        """
        self.core = core

    def get_media_of_other_people(self, tag):
        """
        Returns list of the most recently posted media, excluding our own.
        :param tag: tag to be scanner
        :return: list of recent media objects for tag
        :rtype: list of instabotpatrik.model.InstagramMedia
        """
        return self.core.get_latest_media_by_tag(tag=tag, include_own=False)


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
