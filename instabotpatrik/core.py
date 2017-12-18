import logging
import instabotpatrik


# TODO: rerun tests for timestamp filters, seem like even the tests had wrong verifications.

class InstabotCore:
    def __init__(self, repository, api_client):
        """
        :param repository:
        :type repository: instabotpatrik.repository.BotRepositoryMongoDb
        :param api_client:
        :type api_client: instabotpatrik.client.InstagramClient
        """
        self.repository = repository
        self.api_client = api_client

    def get_latest_media_by_tag(self, tag, include_own):
        """
        :param tag: any string
        :type tag: string
        :param include_own: specifies whether media posted by us should be included in returned list
        :return: list of most recent media for specified tag
        :rtype: list of instabotpatrik.model.InstagramMedia
        """
        recent_media = self.api_client.get_latest_media_by_tag(tag)
        return recent_media if include_own \
            else [media for media in recent_media if media.owner_id != self.api_client.get_our_user().instagram_id]

    # The question here is whether we should call /<media_shortcode/?__a=1 endpoint. Normal user in browser would
    # first click on image thumbnaul, which would call this endpoint, and only after then he would be able to like
    # the picture
    # Taking in consideration experience from https://github.com/instabot-py/instabot.py, it seems like instagram
    # strictly checks this endpoint call order
    def like(self, media):
        """
        :param media:
        :type media: instabotpatrik.model.InstagramMedia
        :return: True if giving like was successfull
        :rtype: bool
        """
        logging.info("[CORE] Want to like.  MediaID:%s MediaShortcode:%s OwnerId:%s",
                     media.instagram_id, media.shortcode, media.owner_id)
        if media.is_liked:
            logging.info("[CORE] MediaID:%s MediaShortcode:%s OwnerId:%s was already liked. Skip this attempt to like.",
                         media.instagram_id, media.shortcode, media.owner_id)
            return True
        else:
            was_liked = self.api_client.like(media.instagram_id)
            if was_liked:
                logging.info("[CORE] Like success. MediaID:%s MediaShortcode:%s OwnerId:%s",
                             media.instagram_id, media.shortcode, media.owner_id)
                media.add_like()
                self.repository.update_media(media)
                owner_user = self.repository.find_user(media.owner_id)
                owner_user = instabotpatrik.model.InstagramUser(media.owner_id) if owner_user is None else owner_user
                owner_user.register_like()
                self.repository.update_user(owner_user)
            else:
                logging.error("[CORE] Liked failure. MediaID:%s MediaShortcode:%s OwnerId:%s", media.instagram_id,
                              media.shortcode,
                              media.owner_id)

        return was_liked

    # def get_user_by_username(self, username):
    #     # TODO : need to do this and use it in follow. Core methods should not require business objects as parameters.
        # Because then it would need to handle whether it can save that object after some changes ar made. But what if that
        # insstance of that object is outdated, compared with what's in the database?
        # Let's assume that people are working with core's interface. It provides information about data at particular moment
        # but it doesn't accept those objects to make modifications on them. The modifications or taking actions against
        # some objects is possible only by providing identifier of that particlar object. Then it's responsibility of
        # core to resolved this data - check database, if it's not there -> call API and store the object.

    def follow(self, user):
        """
        :param user:
        :type user: instabotpatrik.model.InstagramUser
        :return: True if giving follow was successfull
        :rtype: bool
        """

        logging.info("[CORE] Want to follow. Username:%s", user.username)
        if user.detail.we_follow_user:
            logging.info("[CORE] UserID:%s Username:%s is already being followed. Skip this attempt to follow.",
                         user.instagram_id, user.username)
            return True
        else:
            is_followed = self.api_client.follow(user.instagram_id)
            if is_followed:
                logging.info("[CORE] Follow success. Username:%s id:%s", user.username, user.instagram_id)
                user.register_follow()
                self.repository.update_user(user)
                return True
            else:
                logging.error("[CORE] Follow failure. Username:%s id:%s", user.username, user.instagram_id)
                return False

    def unfollow(self, user):
        """
        :param user:
        :type user: instabotpatrik.model.InstagramUser
        :return: True if giving unfollow was successfull
        :rtype: bool
        """
        logging.info("[CORE] Want to unfollow. Username:%s id:%s", user.username, user.instagram_id)
        if not user.detail.we_follow_user:
            logging.info("[CORE] UserID:%s Username:%s is not followed anyway. Skip this attempt to unfollow.",
                         user.instagram_id, user.username)
            return True
        is_unfollowed = self.api_client.unfollow(user.instagram_id)
        if is_unfollowed:
            logging.info("[CORE] Unfollow success. Username:%s id:%s", user.username, user.instagram_id)
            user.register_unfollow()
            self.repository.update_user(user)
            return True
        else:
            logging.error("[CORE] Unfollow failure. Username:%s id:%s", user.username, user.instagram_id)
            return False

    def get_media_owner(self, media, asure_fresh_data=False):
        """
        Tries to find user by instagram_id in DB. If not found, or nothing other than instagram_id is known about
        this user, API is called to fetch details and user details are updated in DB. In the end, it's guaranteed
        that user with details is returned.
        :param media:
        :type media: instabotpatrik.model.InstagramMedia
        :param asure_fresh_data: If Trie, it will be guaranteed data are up to date. If False, data might be outdated
        as stored in the bot's database.
        :type asure_fresh_data: bool
        :return: owner
        :rtype: instabotpatrik.model.InstagramUser
        """
        user = self.repository.find_user(instagram_id=media.owner_id)
        if user is None:
            user = instabotpatrik.model.InstagramUser(instagram_id=media.owner_id)
        if user.is_fully_known() is False or asure_fresh_data:
            if media.owner_username is None:
                media = self.api_client.get_media_detail(media.shortcode)  # display media detail
            user.username = media.owner_username
            self.refresh_user_data(user)
        return user

    def refresh_user_data(self, user):
        """
        Sunchrhonizes user detail with fresh data from Instagram.
        :param user:
        :return:
        """
        if user.username is None:
            raise instabotpatrik.model.InsufficientInformationException(
                "Can't referesh data for user with user_id:%s because his username is not known" % user.instagram_id)
        api_user = self.api_client.get_user_with_details(user.username)  # go to user profile
        user.update_details(api_user)
        self.repository.update_user(user)
        return user

    def refresh_recent_media_for_user(self, user):
        user.recent_media = self.api_client.get_user_with_details(user.username).recent_media

    def get_followed_users(self):
        """
        :return: list of users which we follow
        :rtype: list of instabotpatrik.model.InstagramUser
        """
        return self.repository.find_followed_users()

    def login(self):
        if not self.api_client.is_logged_in():
            self.api_client.login()
