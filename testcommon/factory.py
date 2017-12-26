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


