import logging
import instabotpatrik

class InstabotCore:
    # TODO: Make sure that all actions taken are persistens
    # TODO: Consider what should be stored in case of failure

    def __init__(self, repository, api_client):
        """
        :param repository:
        :type repository: instabotpatrik.repository.BotRepositoryMongoDb
        :param api_client:
        :type api_client: instabotpatrik.client.InstagramClient
        """
        self.repository = repository
        self.api_client = api_client

    def get_latest_media_by_tag(self, tag):
        """
        :param tag: any string
        :type tag: string
        :return: list of most recent media for specified tag
        :rtype: list of instabotpatrik.model.InstagramMedia
        """
        return self.api_client.get_latest_media_by_tag(tag)

    # TODO : handle repository exceptions (create specific exception like "InstaRepositoryException"
    def like(self, media):
        """
        :param media:
        :type media: instabotpatrik.model.InstagramMedia
        :return: True if giving like was successfull
        :rtype: bool
        """
        was_liked = self.api_client.like(media.instagram_id)
        if was_liked:
            media.add_like()
            owner_user = self.repository.find_user_by_instagram_id(media.owner_id)
            owner_user = instabotpatrik.model.InstagramUser() if owner_user is None else owner_user
            owner_user.register_like()
            self.repository.update_media(media)
            self.repository.update_user(owner_user)
        else:
            logging.error("Failed to like: %s of owner %s", media.instagram_id, media.owner_id)
        return was_liked

    def follow(self, user):
        """
        :param user:
        :type user: instabotpatrik.model.InstagramUser
        :return: True if giving follow was successfull
        :rtype: bool
        """
        is_followed = self.api_client.follow(user.id)
        if is_followed:
            logging.info("Following username: %s id: %s", user.username, user.id)
            user.register_follow()
            self.repository.update_user(user)
            return True
        else:
            logging.error("Failed to follow: %s id: %s", user.username, user.id)
            return False

    def unfollow(self, user):
        """
        :param user:
        :type user: instabotpatrik.model.InstagramUser
        :return: True if giving unfollow was successfull
        :rtype: bool
        """
        is_unfollowed = self.api_client.unfollow(user.instagram_id)
        if is_unfollowed:
            logging.info("Unfollowed username: %s id: %s", user.username, user.instagram_id)
            user.register_unfollow()
            self.repository.update_user(user)
            return True
        else:
            logging.error("Failed to unfollow username: %s id: %s", user.username, user.instagram_id)
            return False

    # def get_user_detail_by_id(self, instagram_id):
    #     user = self.repository.find_user_by_id(instagram_id)
    #     if user.username = None
