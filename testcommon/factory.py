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
        count_likes_we_gave=123,
        dt_like=1512845111,
        dt_follow=1512845222,
        dt_unfollow=1512845333):
    """
    :rtype: instabotpatrik.model.InstagramUserBotData
    """
    return instabotpatrik.model.InstagramUserBotData(
        count_likes_we_gave=count_likes_we_gave,
        last_like_datetime=dt_like,
        last_follow_datetime=dt_follow,
        last_unfollow_datetime=dt_unfollow
    )
