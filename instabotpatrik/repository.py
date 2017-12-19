import pymongo
import instabotpatrik
import logging
import dateutil.parser
import dateutil.tz
import pytz


class DataIntegrityException(Exception):
    def __init__(self, message):
        self.message = message


def datetime_to_db_format(dt):
    """
    Converts timezone aware datetime into ISO8601 string in UTC (will end with '+00:00')
    :param dt:
    :type dt: datetime.datetime
    :return:
    """
    if not dt:
        return None
    if dt.tzname() != "UTC":
        dt = dt.astimezone(pytz.UTC)
    return dt.isoformat()


def from_db_to_datetime(time_string):
    """
    Parses string as represented in database into datetime. The returned datetime is timezone aware, in UTC.
    :param time_string:
    :return:
    """
    if time_string is None:
        return None
    if "+00:00" not in time_string:
        raise DataIntegrityException("Wanted to parse timestamp from database, but was from timezone other than UTC!")
    return dateutil.parser.parse(time_string)


def map_user_dict_to_obj(user_dict):
    bot_history = None if user_dict['bot'] is None else instabotpatrik.model.InstagramUserBotData(
        count_likes_we_gave=user_dict['bot']['count_likes_we_gave'],
        last_like_datetime=from_db_to_datetime(user_dict['bot']['dt_like']),
        last_follow_datetime=from_db_to_datetime(user_dict['bot']['dt_follow']),
        last_unfollow_datetime=from_db_to_datetime(user_dict['bot']['dt_unfollow'])
    )
    user_detail = None if user_dict['detail'] is None else instabotpatrik.model.InstagramUserDetail(
        url=user_dict['detail']['url'],
        count_shared_media=user_dict['detail']['count_shared_media'],
        count_follows=user_dict['detail']['count_follows'],
        count_followed_by=user_dict['detail']['count_followed_by'],
        we_follow_user=user_dict['detail']['we_follow_user'],
        user_follows_us=user_dict['detail']['user_follows_us'],
    )
    return instabotpatrik.model.InstagramUser(
        instagram_id=user_dict['instagram_id'],
        username=user_dict['username'],
        user_detail=user_detail,
        bot_data=bot_history
    )


def map_media_dict_to_obj(media_dict):
    return instabotpatrik.model.InstagramMedia(
        instagram_id=media_dict["instagram_id"],
        shortcode=media_dict["shortcode"],
        owner_id=media_dict["owner_id"],
        caption=media_dict["caption"],
        is_liked=media_dict["is_liked"],
        like_count=media_dict["like_count"],
        time_liked=from_db_to_datetime(media_dict["time_liked"]),
        owner_username=media_dict["owner_username"]
    )


def build_user_from_dict(load_from_db):
    def wrapper(*args, **kwargs):
        db_ret = load_from_db(*args, **kwargs)
        if isinstance(db_ret, list):
            return [map_user_dict_to_obj(user) for user in db_ret]
        else:
            return None if db_ret is None else map_user_dict_to_obj(db_ret)

    return wrapper


def build_media_from_dict(load_from_db):
    def wrapper(*args, **kwargs):
        media_dict = load_from_db(*args, **kwargs)
        if isinstance(media_dict, list):
            return [map_media_dict_to_obj(media) for media in media_dict]
        else:
            return None if media_dict is None else map_media_dict_to_obj(media_dict)

    return wrapper


class ConfigRepositoryMongoDb:
    def __init__(self,
                 database_name,
                 config_collection_name,
                 mongo_client):
        """
        :param mongo_client: mongo client instance
        :type mongo_client: pymongo.MongoClient
        """
        self.mongo_client = mongo_client
        self.db = mongo_client[database_name]
        self.config_collection = self.db[config_collection_name]

    def get_tags(self):
        return self.config_collection.find_one(filter={"type": "strategy_select_random_tag"})['tags']

    def get_username(self):
        return self.config_collection.find_one(filter={"type": "credentials"})['username']

    def get_password(self):
        return self.config_collection.find_one(filter={"type": "credentials"})['password']


class BotRepositoryMongoDb:
    def __init__(self,
                 mongo_client,
                 database_name,
                 users_collection_name,
                 media_collection_name):
        """
        :param mongo_client: mongo client instance
        :type mongo_client: pymongo.MongoClient
        """
        self.mongo_client = mongo_client
        self.db = mongo_client[database_name]
        self.users_collection = self.db[users_collection_name]
        self.media_collection = self.db[media_collection_name]

    def update_user(self, user):
        """
        :param user: Save user to database. User is identified by username. If user with such username exists,
        it will be updated. If user with such username is not found, it will be inserted.
        :type user: instabotpatrik.model.InstagramUser
        """
        detail_update = None if user.is_fully_known() is None else {
            "url": user.url,
            "count_shared_media": user.count_shared_media,
            "count_follows": user.count_follows,
            "count_followed_by": user.count_followed_by,
            "we_follow_user": user.we_follow_user,
            "user_follows_us": user.user_follows_us,
        }
        bot_update = {
            "count_likes_we_gave": user.count_likes_we_gave,
            "dt_like": datetime_to_db_format(user.dt_like),
            "dt_follow": datetime_to_db_format(user.dt_follow),
            "dt_unfollow": datetime_to_db_format(user.dt_unfollow)
        }
        update = {
            "$set": {
                "instagram_id": user.instagram_id,
                "username": user.username,
                "detail": detail_update,
                "bot": bot_update
            },
            "$currentDate": {"lastModified": True}
        }
        logging.debug("Going to upsert user:%s", update)
        self.users_collection.update_one(
            filter={"instagram_id": user.instagram_id},
            update=update,
            upsert=True
        )

    @build_user_from_dict
    def find_user_by_username(self, username):
        """
        :param username: load user from database by username
        :rtype: instabotpatrik.model.InstagramUser
        """
        return self.users_collection.find_one(filter={"username": username})

    @build_user_from_dict
    def find_user(self, instagram_id):
        """
        :return: model object representing user
        :rtype: instabotpatrik.model.InstagramUser
        """
        return self.users_collection.find_one(filter={"instagram_id": instagram_id})

    @build_user_from_dict
    def find_followed_users(self):
        """
        :return: users which the bot is following
        :rtype: list of instabotpatrik.model.InstagramUser
        """
        # Lets not fall into premature optimizations here yet...
        return list(self.users_collection.find(filter={"detail.we_follow_user": True}))

    def update_media(self, media):
        """
        :param media: Save media to database. Media is identified by instagram_id.
        If media with such instagram_id exists, it will be updated. Otherwise it will be inserted.
        :type media: instabotpatrik.model.InstagramMedia
        """
        self.media_collection.update_one(
            filter={"instagram_id": media.instagram_id},
            update={
                "$set": {
                    "instagram_id": media.instagram_id,
                    "shortcode": media.shortcode,
                    "owner_id": media.owner_id,
                    "caption": media.caption,
                    "is_liked": media.is_liked,
                    "like_count": media.like_count,
                    "time_liked": datetime_to_db_format(media.time_liked),
                    "owner_username": media.owner_username
                },
                "$currentDate": {"lastModified": True}
            },
            upsert=True
        )

    @build_media_from_dict
    def find_media_by_id(self, media_id):
        """
        :param media_id: instagram_id of media to be loaded
        :type media_id: string
        :return: media object specified by id
        :rtype: instabotpatrik.model.InstagramMedia
        """
        return self.media_collection.find_one(filter={"instagram_id": media_id})
