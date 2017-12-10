import time
import random
import instabotpatrik


class InsufficientInformationException(Exception):
    def __init__(self, message):
        self.message = message


class StrategyFollowBasic:
    def __init__(self, core):
        """
        :type core: instabotpatrik.core.InstabotCore
        """
        self.core = core
        self.max_followed_by = 800
        self.min_followed_by = 10
        self.max_follows = 100
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
        return not user.detail.we_follow_user and \
               (self.min_followed_by < user.detail.we_follow_user < self.max_followed_by) and \
               (self.min_folows < user.detail.count_follows < self.max_follows)


class StrategyLikeBasic:
    def __init__(self):
        """
        :type core: instabotpatrik.core.InstabotCore
        """
        self.media_max_like = 400
        self.media_min_like = 0

    def should_like(self, media):
        """
        :type media: instabotpatrik.model.InstagramMedia
        :rtype: bool
        """
        return media.is_liked is False \
            and (self.media_min_like <= media.like_count <= self.media_max_like)


class StrategyUnfollowBasic:
    def __init__(self, core):
        """
        :param user: user which should be fully known - should have populated details
        :type core: instabotpatrik.core.InstabotCore
        """
        self.we_follow_min_time_sec = 60 * 60 * 50  # follow everyone for at least 50 hours
        self.core = core

    def should_unfollow(self, user):
        """
        Unfollows one or zero of users passed in parameter
        :type user: instabotpatrik.model.InstagramUser
        :rtype: bool
        """
        # TODO: we should not access .detail of user ever, should be private. Instead, give user interface ...
        # TODO: ... for us to access information contained in .detail
        if user.is_fully_known():
            return user.detail.user_follows_us is False \
                and self._follow_time_has_passed(user)
        else:
            raise InsufficientInformationException("User %s is not fully known. StrategyUnfollowBasic can't"
                                                   " determine whether we should follow or not.")

    def _follow_time_has_passed(self, user):
        return time.time() - user.time_we_started_following > self.we_follow_min_time_sec


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


class ActionTimingStrategy:
    def __init__(self):
        print("fo")
