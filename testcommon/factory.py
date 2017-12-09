from testsUnit.context import instabotpatrik


def create_user_detail(
        url="url",
        count_shared_media="count_shared_media",
        count_follows=10,
        count_followed_by=20,
        we_follow_user=True,
        user_follows_us=False):
    """
    :rtype: instabotpatrik.model.InstagramUserDetail
    """
    return instabotpatrik.model.InstagramUserDetail(
        url=url,
        count_shared_media=count_shared_media,
        count_follows=count_follows,
        count_followed_by=count_followed_by,
        we_follow_user=we_follow_user,
        user_follows_us=user_follows_us
    )


def create_bot_data(
        count_likes=123,
        last_like_timestamp=1512845111,
        last_follow_timestamp=1512845222,
        last_unfollow_timestamp=1512845333):
    """
    :rtype: instabotpatrik.model.InstagramUserBotHistory
    """
    return instabotpatrik.model.InstagramUserBotHistory(
        count_likes=count_likes,
        last_like_timestamp=last_like_timestamp,
        last_follow_timestamp=last_follow_timestamp,
        last_unfollow_timestamp=last_unfollow_timestamp
    )
