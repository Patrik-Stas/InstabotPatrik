from testsUnit.context import instabotpatrik
import os
import datetime
import pytz


def get_path_to_file_in_directory_of_this_file(file_name):
    this_directory_absolute = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    return os.path.join(this_directory_absolute, file_name)


def get_config():
    return instabotpatrik.config.Config(config_path=get_path_to_file_in_directory_of_this_file("test.ini"))


def create_repo(config, mongo_client):
    return instabotpatrik.repository.BotRepositoryMongoDb(mongo_client=mongo_client,
                                                          database_name=config.get_db_name(),
                                                          users_collection_name=config.collection_users_name(),
                                                          media_collection_name=config.collection_media_name())


def get_sample_user(instagram_id="user_id", username="username", url="www.foo.bar", count_shared_media=1,
                    count_follows=2, count_followed_by=3, we_follow_user=False,
                    user_follows_us=False):
    detail = instabotpatrik.model.InstagramUserDetail(
        url=url,
        count_shared_media=count_shared_media,
        count_follows=count_follows,
        count_followed_by=count_followed_by,
        we_follow_user=we_follow_user,
        user_follows_us=user_follows_us
    )
    history = instabotpatrik.model.InstagramUserBotData(
        count_likes_we_gave=3,
        last_like_datetime=datetime.datetime(year=2014, month=10, day=10, hour=10, tzinfo=pytz.UTC),
        last_follow_datetime=datetime.datetime(year=2015, month=10, day=10, hour=10, tzinfo=pytz.UTC),
        last_unfollow_datetime=datetime.datetime(year=2016, month=10, day=10, hour=10, tzinfo=pytz.UTC)
    )
    user = instabotpatrik.model.InstagramUser(
        instagram_id=instagram_id,
        username=username,
        user_detail=detail,
        bot_data=history
    )
    return user
