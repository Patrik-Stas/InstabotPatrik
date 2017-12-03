import pymongo
from instabotpatrik.model import InstagramUser


class ConfigRepositoryMongoDb:
    def __init__(self,
                 mongo_client):
        self.mongo_client = mongo_client

    def scan_tags(self):
        return ["a", "b", "c"]

    def get_username(self):
        return "europe.wedding"

    def get_password(self):
        return "_YokyPatrikInstagram54"


class BotRepositoryMongoDb:
    def __init__(self,
                 mongo_client):
        """
        :param mongo_client: blabla
        :type mongo_client: pymongo.MongoClient
        """
        self.mongo_client = mongo_client
        self.database_name = 'instabotpat'
        self.db = mongo_client[self.database_name]

    def update_user(self, user):
        """
        :param user: foo
        :type user: instabotpatrik.model.InstagramUser
        """
        self.db['users'].update_one(
            {"username": user.username},
            {
                "$set": {
                    "instagram_id": user.instagram_id,
                    "url": user.url,
                    "username": user.username,
                    "count_shared_media": user.count_shared_media,
                    "count_follows": user.count_follows,
                    "count_followed_by": user.count_followed_by,
                    "we_follow_user": user.we_follow_user,
                    "user_follows_us": user.user_follows_us,
                    "follow_actions": user.follow_actions,
                    "unfollow_actions": user.unfollow_actions,
                    "like_actions": user.like_actions
                },
                "$currentDate": {"lastModified": True}
            },
            upsert=True
        )

    def update_media(self, media):
        print("Storing: media %s", media.id)

    def load_user(self, instagram_id):
        print("Loading: User %s", instagram_id)

    def load_followed_users(self):
        print("Loading: Followed users %s", id)

    def load_media(self, id):
        print("Loading: media %s", id)
