import instabotpatrik


class InstagramUser:
    def __init__(self,
                 instagram_id,
                 url=None,
                 username=None,
                 count_shared_media=None,
                 count_follows=None,
                 count_followed_by=None,
                 count_given_likes=None,
                 we_follow_user=None,
                 user_follows_us=None,
                 last_like_given_timestamp=None,
                 last_follow_given_timestamp=None,
                 last_unfollow_given_timestamp=None):
        self.instagram_id = instagram_id
        self.url = url
        self.username = username
        self.count_shared_media = count_shared_media
        self.count_follows = count_follows
        self.count_followed_by = count_followed_by
        self.count_given_likes = count_given_likes
        self.we_follow_user = we_follow_user
        self.user_follows_us = user_follows_us
        self.last_like_given_timestamp = last_like_given_timestamp
        self.last_follow_given_timestamp = last_follow_given_timestamp
        self.last_unfollow_given_timestamp = last_unfollow_given_timestamp

    def register_follow(self):
        self.last_follow_given_timestamp = instabotpatrik.tools.get_time()
        self.we_follow_user = True

    def register_unfollow(self):
        self.last_unfollow_given_timestamp = instabotpatrik.tools.get_time()
        self.we_follow_user = False

    def register_like(self):
        self.last_like_given_timestamp = instabotpatrik.tools.get_time()
        if self.count_given_likes is None:
            self.count_given_likes = 1
        else:
            self.count_given_likes += 1


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
