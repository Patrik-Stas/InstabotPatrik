import logging


class InstaBotCore:
    # TODO: Make sure that all actions taken are persistens
    # TODO: Consider what should be stored in case of failure

    def __init__(self, repository, api_client):
        self.repository = repository
        self.api_client = api_client

    def get_media(self, tag):
        return self.api_client.get_media_by_tag(tag)

    # TODO : handle repository exceptions (create specific exception like "InstaRepositoryException"
    def like(self, media):
        was_liked = self.api_client.like(media.id)
        if was_liked:
            logging.info("Liked %s of owner %s", media.id, media.owner)
            self.repository.add_like(media_id=media.id, owner_id=media.owner.id)
        else:
            logging.error("Failed to like: %s of owner %s", media.id, media.owner)
        return was_liked

    def follow(self, user):
        is_followed = self.api_client.follow(user.id)
        if is_followed:
            logging.info("Following username: %s id: %s", user.username, user.id)
            self.repository.add_follow(user)
            return True
        else:
            logging.error("Failed to follow: %s id: %s", user.username, user.id)
            return False

    def unfollow(self, user):
        is_unfollowed = self.api_client.unfollow(user.id)
        if is_unfollowed:
            logging.info("Unfollowed username: %s id: %s", user.username, user.id)
            self.repository.add_unfollow(user)
            return True
        else:
            logging.error("Failed to unfollow username: %s id: %s", user.username, user.id)
            return False
