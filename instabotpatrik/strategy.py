import time
import random
import instabotpatrik
import logging

logging.getLogger().setLevel(20)
logging.basicConfig(format='[%(levelname)s] [%(asctime)s] %(message)s', datefmt='%m/%d/%Y-%H:%M:%S')


class InsufficientInformationException(Exception):
    def __init__(self, message):
        self.message = message


class StrategyFollowBasic:
    def __init__(self):
        self.max_followed_by = 1200
        self.min_followed_by = 6
        self.max_follows = 1200
        self.min_folows = 10

    def should_follow(self, user):
        """
        :param user: user which should be fully known - should have populated details
        :type user: instabotpatrik.model.InstagramUser
        :rtype: bool
        """
        if not user.is_fully_known():
            raise InsufficientInformationException("User %s is not fully known. StrategyFollowBasic can't determine "
                                                   "whether we should follow or not.")
        if user.detail.we_follow_user:
            logging.info("Not going to try to follow user %s. We already follow him.", user.username)
            return False
        if not (self.min_followed_by < user.detail.count_followed_by < self.max_followed_by):
            logging.info("Not going to try to follow user %s. He doesn't fits followed_by count condition." "Followed "
                         "by %d whereas Min:%d Max:%d", user.username, user.detail.count_followed_by,
                         self.min_followed_by, self.max_followed_by)
        if not (self.min_folows < user.detail.count_follows < self.max_follows):
            logging.info("Not going to try to follow user %s. He doesn't fits follows count condition. "
                         "Followed by %d whereas Min:%d Max:%d", user.username, user.detail.count_follows,
                         self.min_folows, self.max_follows)
            return False
        return True


class StrategyLikeBasic:
    def __init__(self):
        self.media_max_like = 400
        self.media_min_like = 0

    def should_like(self, media):
        """
        :type media: instabotpatrik.model.InstagramMedia
        :rtype: bool
        """
        if media.is_liked:
            logging.info("Media shortcode %s is already liked", media.shortcode)
            return False
        if not (self.media_min_like <= media.like_count <= self.media_max_like):
            logging.info("Media shortcode %s doesn't fit like count condition. Has %d likes. LimitMin:%d, LimitMax:%d",
                         media.shortcode, media.like_count, self.media_min_like, self.media_max_like)
            return False
        return True


class StrategyUnfollowBasic:
    def __init__(self):
        self.we_follow_min_time_sec = 60 * 60 * 50  # follow everyone for at least 50 hours

    def should_unfollow(self, user):
        """
        Unfollows one or zero of users passed in parameter
        :type user: instabotpatrik.model.InstagramUser
        :rtype: bool
        """
        # TODO: we should not access .detail of user ever, should be private. Instead, give user interface ...
        # TODO: ... for us to access information contained in .detail
        if user.is_fully_known():
            if not user.detail.user_follows_us and self._follow_time_has_passed(user):
                logging.info("We can unfollow %s cause he doesn't follow us, and we followed him long enough.",
                             user.username)
                return True
            else:
                return False
        else:
            raise InsufficientInformationException("User %s is not fully known. StrategyUnfollowBasic can't"
                                                   " determine whether we should follow or not.")

    def _follow_time_has_passed(self, user):
        return time.time() - user.detail.time_we_started_following > self.we_follow_min_time_sec


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
