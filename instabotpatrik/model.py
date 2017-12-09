import instabotpatrik
import logging
from copy import deepcopy


class InstagramUserBotHistory:

    def __init__(self,
                 count_likes=None,
                 last_like_timestamp=None,
                 last_follow_timestamp=None,
                 last_unfollow_timestamp=None):
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
                 user_detail=None):
        """

        :type user_detail: InstagramUserDetail
        :type bot_history: InstagramUserBotHistory
        """
        self.instagram_id = instagram_id
        self.username = username
        self.detail = user_detail
        self.bot_data = bot_history if bot_history is not None else InstagramUserBotHistory()

    def is_fully_known(self):  # Information available if user profile is viewed
        return self.instagram_id is not None \
               and self.username is not None \
               and self.detail is not None

    def update_data(self, source_user):
        """
        :param source_user: source of new information
        :type source_user: InstagramUser
        """
        if source_user.is_fully_known():
            if self.instagram_id != source_user.instagram_id:
                raise Exception("updating information on user(%s) from user with different ID(%s) doesnt. make sense.",
                                self.instagram_id, source_user.instagram_id)
        self.username = source_user.username
        self.detail = deepcopy(source_user.detail)

    def register_follow(self):
        self.bot_data.last_follow_timestamp = instabotpatrik.tools.get_time()
        self.detail.we_follow_user = True

    def register_unfollow(self):
        self.bot_data.last_unfollow_timestamp = instabotpatrik.tools.get_time()
        self.detail.we_follow_user = False

    def register_like(self):
        self.bot_data.last_like_timestamp = instabotpatrik.tools.get_time()
        if self.bot_data.count_likes is None:
            self.bot_data.count_likes = 1
        else:
            self.bot_data.count_likes += 1


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
        self.instagram_id = instagram_id
        self.shortcode = shortcode
        self.owner_id = owner_id
        self.caption = caption
        self.is_liked = is_liked
        self.like_count = like_count
        self.time_liked = time_liked
        self.owner_username = owner_username

    def add_like(self):
        self.time_liked = instabotpatrik.tools.get_time()
        self.is_liked = True
