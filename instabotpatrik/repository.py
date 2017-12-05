import pymongo
import instabotpatrik


def build_user_from_dict(load_from_db):
    def wrapper(*args, **kwargs):
        user_dict = load_from_db(*args, **kwargs)
        user = instabotpatrik.model.InstagramUser(
            instagram_id=user_dict['instagram_id'],
            url=user_dict['url'],
            username=user_dict['username'],
            count_shared_media=user_dict['count_shared_media'],
            count_follows=user_dict['count_follows'],
            count_followed_by=user_dict['count_followed_by'],
            we_follow_user=user_dict['we_follow_user'],
            user_follows_us=user_dict['user_follows_us'],
            follow_actions=user_dict['follow_actions'],
            unfollow_actions=user_dict['unfollow_actions'],
            like_actions=user_dict['like_actions']
        )
        return user

    return wrapper


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
                 mongo_client,
                 database_name,
                 users_collection_name,
                 media_collection_name):
        """
        :param mongo_client: blabla
        :type mongo_client: pymongo.MongoClient
        """
        self.mongo_client = mongo_client
        self.db = mongo_client[database_name]
        self.users_collection = self.db[users_collection_name]
        self.media_collection = self.db[media_collection_name]

    def update_user(self, user):
        """
        :param user: Save user to database. User is identified by username. If user with such username exists, it will be updated.
        If user with such username is not found, it will be inserted.
        :type user: instabotpatrik.model.InstagramUser
        """
        self.users_collection.update_one(
            filter={"username": user.username},
            update={
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

    @build_user_from_dict
    def load_user_by_username(self, username):
        """
        :param username: load user from database by username
        :rtype: instabotpatrik.model.InstagramUser
        """
        return self.users_collection.find_one(filter={"username": username})

    @build_user_from_dict
    def load_user_by_instagram_id(self, instagram_id):
        """
        :return: model object representing user
        :rtype: instabotpatrik.model.InstagramUser
        """
        fo = self.users_collection.find_one(filter={"instagram_id": instagram_id})
        print(str(fo))
        return fo

    def update_media(self, media):
        """
        :param media: Save media to database. Media is identified by instagram_id.
        If media with such instagram_id exists, it will be updated. Otherwise it will be inserted.
        :type media: instabotpatrik.model.InstagramMedia
        """
        print("Storing: media %s", media.instagram_id)

    def load_followed_users(self):
        """
        :return: list of users which the bot is following
        :rtype: list of instabotpatrik.model.InstagramUser
        """
        print("Loading: Followed users %s", id)
        return []

    def load_media(self, id):
        """
        :param id: instagram_id of media to be loaded
        :type id: string
        :return: media object specified by id
        :rtype: list of instabotpatrik.model.InstagramMedia
        """
        print("Loading: media %s", id)
        return []
