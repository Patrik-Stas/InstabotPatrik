import random
import logging
import instabotpatrik
import time


class LfsWorkflow:
    def __init__(self, user_controller, media_controller):
        """
        :param user_controller:
        :type user_controller: instabotpatrik.core.UserController
        :param media_controller:
        :type media_controller: instabotpatrik.core.MediaController
        """
        self.user_controller = user_controller
        self.media_controller = media_controller
        self.lfs_likes_for_user_min = 1
        self.lfs_likes_for_user_max = 4
        self.liking_session_like_delay_min_sec = 3
        self.liking_session_like_delay_max_sec = 20

        self.dt_like_filter = instabotpatrik.filter.LastLikeFilter(more_than_hours_ago=24 * 2)
        self.dt_follow_filter = instabotpatrik.filter.LastFollowFilter(more_than_hours_ago=24 * 2)
        self.dt_unfollow_filter = instabotpatrik.filter.LastUnfollowFilter(more_than_hours_ago=24 * 7)

        self.followed_by_filter = instabotpatrik.filter.UserFollowedByCountFilter(min_followed_by=6,
                                                                                  max_followed_by=1500)
        self.follows_filter = instabotpatrik.filter.UserFollowsCountFilter(min_follows=6, max_follows=1200)

    def is_approved_for_lfs(self, user):
        return self.dt_follow_filter.passes(user) \
               and self.dt_unfollow_filter.passes(user) \
               and self.dt_like_filter.passes(user) \
               and self.followed_by_filter.passes(user) \
               and self.follows_filter.passes(user)

    def _wait_before_new_like(self, media_owner):
        sleepsec = random.randint(self.liking_session_like_delay_min_sec, self.liking_session_like_delay_max_sec)
        logging.info("LFS in progress [user_id:%s username:%s] Will wait %d seconds before giving next like.",
                     media_owner.instagram_id, media_owner.username, sleepsec)
        time.sleep(sleepsec)

    def _wait_before_new_follow(self, media_owner):
        sleepsec = random.randint(self.liking_session_like_delay_min_sec, self.liking_session_like_delay_max_sec)
        logging.info("LFS in progress [user_id:%s username:%s] Will wait %d seconds before following this user.",
                     media_owner.instagram_id, media_owner.username, sleepsec)
        time.sleep(sleepsec)

    def run(self, media, media_owner):
        """
        :type media: instabotpatrik.model.InstagramMedia
        :type media_owner: instabotpatrik.model.InstagramUser
        :return:
        """
        logging.info("[LFS] Starting: User ID:%s Username:%s. Media shortcode %s",
                     media_owner.instagram_id, media_owner.username, media.shortcode)
        # give like to "found" media he posted
        self.media_controller.like(media_id=media.instagram_id, shortcode=media.shortcode)

        # take a look at his profile
        user_recent_media = self.media_controller.get_recent_media_for_user(username=media_owner.username)

        # pick randomly posts he recently posted which we'll like in this LFS
        like_count = random.randint(self.lfs_likes_for_user_min, self.lfs_likes_for_user_max)
        like_count = min(like_count, len(user_recent_media))
        logging.info("[LFS] User has %d recent medias. We will pick random %d pieces to like.",
                     len(user_recent_media), like_count)

        medias_to_like = random.sample(user_recent_media, like_count)
        logging.info("[LFS] Following media will be liked %s", [media.shortcode for media in medias_to_like])

        # like his media
        likes_given = 0
        for media_to_like in medias_to_like:
            self._wait_before_new_like(media_owner)
            if self.media_controller.like(media_id=media_to_like.instagram_id, shortcode=media_to_like.shortcode):
                likes_given += 1

        logging.info("[LFS] Liking finished, let's follow him if we don't.")
        if media_owner.we_follow_user is False:
            self.user_controller.follow(instagram_id=media_owner.instagram_id)

        logging.info("[LFS] Finished. [user_id::%s username:%s] Gave %d likes.",
                     media_owner.instagram_id, media_owner.username, likes_given)


class UnfollowWorkflow:
    def __init__(self, user_controller):
        """
        :param core:
        :type core: instabotpatrik.core.UserController
        """
        self.user_controller = user_controller
        self.dt_follow_filter = instabotpatrik.filter.LastFollowFilter(more_than_hours_ago=24 * 2)

    def find_user_to_unfollow(self):
        followed_users = self.user_controller.get_followed_users()

        for user in followed_users:
            if self.dt_follow_filter.passes(user):
                self.user_controller.get_fresh_user(username=user.username)
                if user.user_follows_us is False:
                    return user
        return None

    def run(self):
        user_to_unfollow = self.find_user_to_unfollow()
        if user_to_unfollow is not None:
            self.user_controller.unfollow(instagram_id=user_to_unfollow)
        else:
            logging.info("No suitable user for unfollow was found")

    # def handle_single_media_like(self, media):
    #     logging.info("Handling likes for media %s", media.shortcode)
    #     if self.action_manager.is_action_allowed_now("like"):
    #         return
    #     if self.strategy_like.should_like(media):
    #         if self.core.like(media):
    #             self.action_manager.allow_action_after_seconds('like', self.like_delay_sec)

    # def like_recent_media(self, user, likes_min=1, likes_max=5):
    #     """
    #     Likes randomly picked recent medias, including for sure the very last media posted.
    #     :param user:
    #     :type user: instabotpatrik.model.InstagramUser
    #     :param likes_min:
    #     :param likes_max:
    #     :return:
    #     """
    #     give_likes = random.randint(likes_min, likes_max)
    #     media_to_like = random.sample(user.recent_media, give_likes)
    #     if user.recent_media[0] not in media_to_like:
    #         media_to_like[0] = user.recent_media[0]
    #     likes_given_count = 0
    #     for media in media_to_like:
    #         if self.like(media):
    #             likes_given_count += 1
    #     return likes_given_count

    # def handle_user_follow(self, user):
    #     logging.info("Handling follow for user %s", user.username)
    #     if self.action_manager.is_action_allowed_now("follow") and self.strategy_follow.should_follow(user):
    #         if self.core.follow(user):
    #             self.action_manager.allow_action_after_seconds('follow', self.follow_delay_sec)