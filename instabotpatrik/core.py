import logging
import instabotpatrik

logging.getLogger().setLevel(20)
logging.basicConfig(format='[%(levelname)s] [%(asctime)s] %(message)s', datefmt='%m/%d/%Y-%H:%M:%S')


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
            else [media for media in recent_media if media.owner_id != self.api_client.our_instagram_id]

    def like(self, media):
        """
        :param media:
        :type media: instabotpatrik.model.InstagramMedia
        :return: True if giving like was successfull
        :rtype: bool
        """
        logging.info("[CORE] Want to like.  MediaID:%s MediaShortcode:%s OwnerId:%s", media.instagram_id,
                     media.shortcode,
                     media.owner_id)
        was_liked = self.api_client.like(media.instagram_id)
        if was_liked:
            logging.info("[CORE] Like success. MediaID:%s MediaShortcode:%s OwnerId:%s", media.instagram_id,
                         media.shortcode,
                         media.owner_id)
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

    def follow(self, user):
        """
        :param user:
        :type user: instabotpatrik.model.InstagramUser
        :return: True if giving follow was successfull
        :rtype: bool
        """
        logging.info("[CORE] Want to follow. Username:%s id:%s", user.username, user.instagram_id)
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
        is_unfollowed = self.api_client.unfollow(user.instagram_id)
        if is_unfollowed:
            logging.info("[CORE] Unfollow success. Username:%s id:%s", user.username, user.instagram_id)
            user.register_unfollow()
            self.repository.update_user(user)
            return True
        else:
            logging.error("[CORE] Unfollow failure. Username:%s id:%s", user.username, user.instagram_id)
            return False

    def get_media_owner(self, media):
        """
        Tries to find user by instagram_id in DB. If not found, or nothing other than instagram_id is known about
        this user, API is called to fetch details and user details are updated in DB. In the end, it's guaranteed
        that user with details is returned.
        :param media:
        :type media: instabotpatrik.model.InstagramMedia
        :return: owner
        :rtype: instabotpatrik.model.InstagramUser
        """
        try:
            user = self.repository.find_user(instagram_id=media.owner_id)
            if user is None:
                user = instabotpatrik.model.InstagramUser(instagram_id=media.owner_id)
            if user.is_fully_known() is False:
                media = self.api_client.get_media_detail(media.shortcode)  # display media detail
                api_user = self.api_client.get_user_with_details(media.owner_username)  # go to user profile
                user.update_data(api_user)
                self.repository.update_user(user)
            return user
        except Exception as e:
            logging.error(e, exc_info=True)
            return None
