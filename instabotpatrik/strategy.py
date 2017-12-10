import time
import random
import instabotpatrik


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

    def _can_follow(self, user):
        """
        :param user:
        :type user: instabotpatrik.model.InstagramUser
        :return:
        """
        # TODO: We need to consider situation when detail is None. Maybe someone passed users with only id and history, without details
        return not user.detail.we_follow_user and \
               (self.min_followed_by < user.detail.we_follow_user < self.max_followed_by) and \
               (self.min_folows < user.detail.count_follows < self.max_follows)

    def follow(self, users):
        """
        :param users:
        :type users: list of instabotpatrik.model.InstagramUser
        :return:
        """
        for user in users:
            if self._can_follow(user):
                if self.core.follow(user):
                    return True
        return False


class StrategyLikeBasic:
    def __init__(self, core):
        """
        :type core: instabotpatrik.core.InstabotCore
        """
        self.media_max_like = 120
        self.media_min_like = 0
        self.core = core

    def like(self, medias):
        """
        Like one of the medias
        :type medias: list of instabotpatrik.model.InstagramMedia
        :return:
        """
        for media in medias:
            if media.is_liked is False and (self.media_min_like <= media.like_count <= self.media_max_like):
                if self.core.like(media):
                    return True
        return False


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


class StrategyUnfollowBasic:
    def __init__(self, core):
        """
        :type core: instabotpatrik.core.InstabotCore
        """
        self.we_follow_min_time_sec = 60 * 60 * 50  # follow everyone for at least 50 hours
        self.core = core

    def unfollow(self, followed_users):
        """
        Unfollows one or zero of users passed in parameter
        :param followed_users:
        :type followed_users: list of instabotpatrik.model.InstagramUser
        :return: Number of accounts unfollowed
        """
        followed_count = 0
        for user in followed_users:
            if user.user_follows_us is False and self._follow_time_has_passed(user):
                if self.core.unfollow(user):
                    followed_count += 1
                    break
        return followed_count

    def _follow_time_has_passed(self, user):
        return time.time() - user.time_we_started_following > self.we_follow_min_time_sec


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
