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
                 follow_actions=[],
                 unfollow_actions=[],
                 like_actions=[],
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
        self.follow_actions = follow_actions
        self.unfollow_actions = unfollow_actions
        self.like_actions = like_actions
        self.last_like_given_timestamp = last_like_given_timestamp
        self.last_follow_given_timestamp = last_follow_given_timestamp
        self.last_unfollow_given_timestamp = last_unfollow_given_timestamp

    def add_follow(self, timestamp):
        self.like_actions.append({"timestamp": timestamp})
        # insert / update existing record

    def add_unfollow(self, timestamp):
        self.unfollow_actions.append({"timestamp": timestamp})
        # insert / update existing record

    def add_like(self, timestamp, media_id):
        self.actions.append({"timestamp": timestamp, "media_id": media_id})
        # insert / update existing record

    def get_follow_actions(self):
        return [action for action in self.actions if action.action_type == "follow"]

    def get_last_follow_action(self):
        follow_actions = self.get_follow_actions()
        return None \
            if len(follow_actions) == 0 \
            else sorted(self.get_follow_actions(), key=lambda action: action.timestamp)[0]

    def get_unfollow_actions(self):
        return [action for action in self.actions if action.action_type == "unfollow"]

    def get_last_unfollow_action(self):
        unfollow_actions = self.get_unfollow_actions()
        return None \
            if len(unfollow_actions) == 0 \
            else sorted(self.get_unfollow_actions(), key=lambda action: action.timestamp)[0]

    def get_like_actions(self):
        return [action for action in self.actions if action.action_type == "like"]

    def get_last_like_action(self):
        like_actions = self.get_like_actions()
        return None \
            if len(like_actions) == 0 \
            else sorted(self.get_like_actions(), key=lambda action: action.timestamp)[0]


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
