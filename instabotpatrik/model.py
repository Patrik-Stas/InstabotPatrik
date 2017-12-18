import instabotpatrik
from copy import deepcopy
import logging


class InsufficientInformationException(Exception):
    def __init__(self, message):
        self.message = message


class InstagramUserBotHistory:

    def __init__(self,
                 count_likes=None,
                 last_like_timestamp=None,
                 last_follow_timestamp=None,
                 last_unfollow_timestamp=None):
        """
        :param count_likes:
        :type count_likes: int
        :param last_like_timestamp:
        :type last_like_timestamp: datetime.datetime
        :param last_follow_timestamp:
        :type last_follow_timestamp: datetime.datetime
        :param last_unfollow_timestamp:
        :type last_unfollow_timestamp: datetime.datetime
        """
        self.count_likes = count_likes
        self.last_like_timestamp = last_like_timestamp
        self.last_follow_timestamp = last_follow_timestamp
        self.last_unfollow_timestamp = last_unfollow_timestamp


class InstagramUserDetail:

    def __init__(self,
                 url,
                 count_shared_media,
                 count_follows,
                 count_followed_by,
                 we_follow_user,
                 user_follows_us):
        self.url = url
        self.count_shared_media = count_shared_media
        self.count_follows = count_follows
        self.count_followed_by = count_followed_by
        self.we_follow_user = we_follow_user
        self.user_follows_us = user_follows_us


class InstagramUser:

    def __init__(self,
                 instagram_id,
                 bot_history=None,
                 username=None,
                 user_detail=None,
                 recent_media=[]):
        """

        :type user_detail: InstagramUserDetail
        :type bot_history: InstagramUserBotHistory
        """
        self.instagram_id = instagram_id
        self.username = username
        self._detail = user_detail
        self._bot_data = bot_history if bot_history is not None else InstagramUserBotHistory()
        self.recent_media = recent_media

    @property
    def detail(self):
        """
        :return:
        :rtype: InstagramUserDetail
        """
        return self._detail

    @property
    def bot_data(self):
        """
        :return:
        :rtype: InstagramUserBotHistory
        """
        return self._bot_data

    def is_fully_known(self):  # Information available if user profile is viewed
        return self.instagram_id is not None \
               and self.username is not None \
               and self._detail is not None

    def update_details(self, source_user):
        """
        :param source_user: source of new information
        :type source_user: InstagramUser
        """
        if source_user.is_fully_known():
            if self.instagram_id != source_user.instagram_id:
                raise Exception("updating information on user(%s) from user with different ID(%s) doesnt. make sense.",
                                self.instagram_id, source_user.instagram_id)
        self.username = source_user.username
        self._detail = deepcopy(source_user._detail)

    def register_follow(self):
        self._bot_data.last_follow_timestamp = instabotpatrik.tools.get_utc_datetime()
        self._detail.we_follow_user = True
        logging.debug("Registered follow user_id:%s username:%s.")

    def register_unfollow(self):
        self._bot_data.last_unfollow_timestamp = instabotpatrik.tools.get_utc_datetime()
        self._detail.we_follow_user = False
        logging.debug("Registered unfollow user_id:%s username:%s")

    def register_like(self):
        self._bot_data.last_like_timestamp = instabotpatrik.tools.get_utc_datetime()
        if self.bot_data.count_likes is None:
            self._bot_data.count_likes = 1
        else:
            self._bot_data.count_likes += 1
        logging.debug("Registered like for user_id:%s username:%s. He has now %d likes",
                      self.instagram_id, self.username, self.bot_data.count_likes)


class InstagramMedia:
    def __init__(self,
                 instagram_id,
                 shortcode,
                 owner_id,
                 caption,
                 like_count=None,
                 owner_username=None,
                 is_liked=None,
                 time_liked=None):
        self._instagram_id = instagram_id
        self._shortcode = shortcode
        self._owner_id = owner_id
        self._caption = caption
        self._is_liked = is_liked
        self._like_count = like_count
        self._time_liked = time_liked
        self._owner_username = owner_username

    @property
    def instagram_id(self):
        return self._instagram_id

    @property
    def shortcode(self):
        return self._shortcode

    @property
    def owner_id(self):
        return self._owner_id

    @property
    def caption(self):
        return self._caption

    @property
    def is_liked(self):
        return self._is_liked

    @property
    def like_count(self):
        return self._like_count

    @property
    def time_liked(self):
        return self._time_liked

    @property
    def owner_username(self):
        return self._owner_username

    def add_like(self):
        self._time_liked = instabotpatrik.tools.get_utc_datetime()
        self._is_liked = True
