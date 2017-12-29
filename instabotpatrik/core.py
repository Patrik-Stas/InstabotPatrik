import logging

import instabotpatrik


class InstabotException(Exception):
    def __init__(self, message):
        self.message = message


class AccountController:
    def __init__(self, repository, api_client):
        """
        :param repository:
        :type repository: instabotpatrik.repository.BotRepositoryMongoDb
        :param api_client:
        :type api_client: instabotpatrik.client.InstagramClient
        """
        self.repository = repository
        self.api_client = api_client

    def login(self):
        if not self.api_client.is_logged_in():
            self.api_client.login()

    def get_our_user(self):
        return self.api_client.get_our_user()

    def get_our_username(self):
        return self.api_client.user_login


class UserController:
    def __init__(self, repository, api_client):
        """
        :param repository:
        :type repository: instabotpatrik.repository.BotRepositoryMongoDb
        :param api_client:
        :type api_client: instabotpatrik.client.InstagramClient
        """
        self.repository = repository
        self.api_client = api_client
        self.logger = logging.getLogger(self.__class__.__name__)

    def follow(self, instagram_id):
        """
        :param instagram_id:
        :type instagram_id: str
        :return: True if giving follow was successfull
        :rtype: bool
        """
        user = self.get_user_by_id(instagram_id)
        self.logger.info("Want to follow. Username:%s", user.username)
        if user.we_follow_user:
            self.logger.info("UserID:%s Username:%s is already being followed. Skip this attempt to follow.",
                         user.instagram_id, user.username)
        else:
            is_followed = self.api_client.follow(user.instagram_id)
            if is_followed:
                self.logger.info("Follow success. Username:%s id:%s", user.username, user.instagram_id)
                user.register_follow()
                self.repository.update_user(user)
            else:
                raise InstabotException("Follow failure. Username:%s id:%s" % (user.username, user.instagram_id))

    def unfollow(self, instagram_id):
        """
        :param instagram_id:
        :type instagram_id: str
        :return: True if giving unfollow was successfull
        :rtype: bool
        """
        self.logger.info("Want to unfollow. id:%s", instagram_id)
        user = self.get_user_by_id(instagram_id)
        if not user.we_follow_user:
            self.logger.info("UserID:%s Username:%s is not followed anyway. Skip this attempt to unfollow.",
                         user.instagram_id, user.username)
            return
        is_unfollowed = self.api_client.unfollow(user.instagram_id)
        if is_unfollowed:
            self.logger.info("Unfollow success. Username:%s id:%s", user.username, user.instagram_id)
            user.register_unfollow()
            self.repository.update_user(user)
        else:
            raise InstabotException("Unfollow failure. Username:%s id:%s" % (user.username, user.instagram_id))

    def get_media_owner(self, media_shortcode, asure_fresh_data=False):
        """
        Tries to find user by instagram_id in DB. If not found, or nothing other than instagram_id is known about
        this user, API is called to fetch details and user details are updated in DB. In the end, it's guaranteed
        that user with details is returned.
        :param media_shortcode:
        :type media_shortcode: str
        :param asure_fresh_data: If Trie, it will be guaranteed data are up to date. If False, data might be outdated
        as stored in the bot's database.
        :type asure_fresh_data: bool
        :return: owner
        :rtype: instabotpatrik.model.InstagramUser
        """
        media = self.api_client.get_media_detail(media_shortcode)  # display media detail
        self.repository.update_media(media)
        db_user = self.get_user_by_id(media.owner_id)
        if not db_user or asure_fresh_data:
            self._refresh_user_data(media.owner_username)
            return self.repository.find_user_by_username(media.owner_username)
        else:
            return db_user

    def get_user_by_id(self, instagram_id):
        return self.repository.find_user(instagram_id=instagram_id)

    def get_fresh_user(self, username):
        self._refresh_user_data(username)
        return self.repository.find_user_by_username(username)

    def _refresh_user_data(self, username):
        """
        Sunchrhonizes user detail with fresh data from Instagram.
        :param username:
        """
        if not username:
            raise instabotpatrik.model.InsufficientInformationException('Username is "None".')
        user = self.repository.find_user_by_username(username=username)
        api_user = self.api_client.get_user_with_details(username=username)
        if user:
            user.update_details(api_user)
        else:
            user = api_user
        self.repository.update_user(user)

    def get_followed_users(self):
        """
        :return: list of users which we follow
        :rtype: list of instabotpatrik.model.InstagramUser
        """
        return self.repository.find_followed_users()


class MediaController:
    def __init__(self, repository, api_client):
        """
        :param repository:
        :type repository: instabotpatrik.repository.BotRepositoryMongoDb
        :param api_client:
        :type api_client: instabotpatrik.client.InstagramClient
        """
        self.repository = repository
        self.api_client = api_client
        self.logger = logging.getLogger(self.__class__.__name__)

    def get_recent_media_by_tag(self, tag, excluded_owner_usernames=[]):
        """
        :param tag: any string
        :type tag: string
        :param excluded_owner_usernames
        :return: list of most recent media for specified tag
        :rtype: list of instabotpatrik.model.InstagramMedia
        """
        return [media for media in self.api_client.get_recent_media_by_tag(tag)
                if media.owner_username not in excluded_owner_usernames]

    def get_recent_media_for_user(self, username):
        """
        :param username:
        :return:
        :rtype: list of instabotpatrik.model.InstagramMedia
        """
        return self.api_client.get_recent_media_of_user(username)

    def like(self, media_id, shortcode):
        """
        :param media_id:
        :type media_id: str
        :param shortcode
        :return: True if giving like was successfull
        """
        self.logger.info("Want to like. MediaID:%s", media_id)
        media = self.repository.find_media_by_id(media_id=media_id)
        if not media:
            media = self.api_client.get_media_detail(shortcode_media=shortcode)
            self.repository.update_media(media)
        if media.is_liked:
            self.logger.info("MediaID:%s MediaShortcode:%s OwnerId:%s was already liked. "
                         "Skip this attempt to like.", media.instagram_id, media.shortcode, media.owner_id)
        else:
            like_success = self.api_client.like(media_id)
            if like_success:
                self.logger.info("Like success. MediaID:%s MediaShortcode:%s OwnerId:%s",
                             media.instagram_id, media.shortcode, media.owner_id)
                media.add_like()
                self.repository.update_media(media)
                owner_user = self.repository.find_user(media.owner_id)
                owner_user = instabotpatrik.model.InstagramUser(media.owner_id) if owner_user is None else owner_user
                owner_user.register_like()
                self.repository.update_user(owner_user)
            else:
                raise InstabotException("Liked failure. MediaID:%s MediaShortcode:%s OwnerId:%s"
                                        % (media.instagram_id, media.shortcode, media.owner_id))
