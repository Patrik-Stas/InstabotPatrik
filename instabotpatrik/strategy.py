import time
import random
import instabotpatrik


# TODO: This needs to be udpated -we are using insta core now
class StrategyFollowBasic:
    def __init__(self, core):
        """
        :type core: instabotpatrik.core.InstabotCore
        """
        self.core = core
        self.max_followers = 5000
        self.min_followers = 10
        self.min_ration = 0.6
        self.last_follow_time = time.time()

    def follow(self):
        if self.is_action_allowed_now("follow"):
            self.write_log("Keep calm - It's your own profile ;)")
            return
        log_string = "Trying to follow: %s" % (self.media_by_tag[0]["owner"]["id"])
        self.write_log(log_string)

        if self.follow(self.media_by_tag[0]["owner"]["id"]) != False:
            follow_record = {"user:": self.media_by_tag[0]["owner"]["id"], "follow_time": time.time()}
            self.bot_follow_list.append(follow_record)
            self.next_iteration["follow"] = time.time() + self.add_time(self.follow_delay)


class StrategyLikeBasic:
    def __init__(self, core):
        """
        :type core: instabotpatrik.core.InstabotCore
        """
        self.media_max_like = 50
        self.media_min_like = 0
        self.core = core

    def is_like_count_compliant(self, media_node_dict):
        like_count = media_node_dict['likes']['count']
        return ((self.media_min_like <= like_count <= self.media_max_like) or
                (self.media_max_like == 0 and like_count >= self.media_min_like) or
                (self.media_min_like == 0 and like_count <= self.media_max_like) or
                (self.media_min_like == 0 and self.media_max_like == 0))

    def like(self, media_nodes_dict):
        for media_node in media_nodes_dict:
            if self.core.do_we_like(media_node['id']):
                continue
            if not self.is_like_count_compliant(media_node):
                continue
            else:
                self.core.like(media_node)


class StrategyMediaScanBasic:
    def __init__(self, core):
        """
        :type core: instabotpatrik.core.InstabotCore
        """
        self.scan_frequency_sec = 10 * 60
        self.core = core

    def get_media(self, tag):
        return self.core.get_media_id_by_tag(tag)


class StrategyUnfollowBasic:
    def __init__(self, core):
        """
        :type core: instabotpatrik.core.InstabotCore
        """
        self.last_unfollow_time = time.time()
        self.we_follow_min_time_sec = 60 * 60 * 50  # follow everyone for at least 50 hours
        self.core = core

    def unfollow(self, followed_users):
        for user in followed_users:
            if self._should_unfollow(user):
                if self.core.register_unfollow(user):
                    self.last_unfollow_time = time.time()

    @staticmethod
    def _is_selebgram(user):
        return user.count_follows == 0 or user.count_followed_by / user.count_follows > 2

    @staticmethod
    def _is_fake(user):
        return user.count_followed_by == 0 or user.count_follows / user.count_followed_by > 2

    @staticmethod
    def _is_active(user):
        return user.count_shared_media > 0 \
               and user.count_follows / user.count_shared_media < 10 \
               and user.count_followed_by / user.count_shared_media < 10

    @staticmethod
    def _follow_time_has_pass(user):
        return time.time() - user.time_we_started_following

    def _should_unfollow(self, user):
        return self._is_selebgram(user) or \
               self._is_fake(user) or (self._is_active(user) is False) or \
               (user.user_follows_us is False)


class StrategyTagSelectionBasic:
    def __init__(self, get_candidate_tags):
        """
        :param get_candidate_tags: callable which returns list of strings (tags)
        :type get_candidate_tags: collections.abc.Callable
        """
        self.callable_get_tags = get_candidate_tags

    def get_tag(self):
        """:rtype: string"""
        tags = self.callable_get_tags()
        return random.choice(tags)
