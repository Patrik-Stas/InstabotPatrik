#  TODO: Need to try creating, persisting, loading, modifying, persisting and loading
class InstagramUser:
    def __init__(self,
                 instagram_id,
                 url,
                 username,
                 count_shared_media,
                 count_follows,
                 count_followed_by,
                 we_follow_user,
                 user_follows_us,
                 last_like_given_timestamp=None,
                 last_follow_given_timestamp=None,
                 last_unfollow_given_timestamp=None):
        self.instagram_id = instagram_id
        self.url = url
        self.username = username
        self.count_shared_media = count_shared_media
        self.count_follows = count_follows
        self.count_followed_by = count_followed_by
        self.we_follow_user = we_follow_user
        self.user_follows_us = user_follows_us
        self.last_like_given_timestamp = last_like_given_timestamp
        self.last_follow_given_timestamp = last_follow_given_timestamp
        self.last_unfollow_given_timestamp = last_unfollow_given_timestamp


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

    def __str__(self):
        return "id:%s hortcode:%s owner_id:%s caption:%s" % (
        self.instagram_id, self.shortcode, self.owner_id, self.caption)
