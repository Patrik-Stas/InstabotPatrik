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

        self.min_like_delay_hours = 48
        self.min_follow_delay_hours = 48
        self.min_unfollow_delay_hours = 24 * 10  # start LFS again no sooner than 10 days after last unfollow
        self.min_count_followed_by = 6
        self.max_count_followed_by = 1500

        self.min_count_follows = 6
        self.max_count_follows = 1200

        self.dt_like_filter = instabotpatrik.filter.LastLikeFilter(more_than_hours_ago=self.min_like_delay_hours)
        self.dt_follow_filter = instabotpatrik.filter.LastFollowFilter(more_than_hours_ago=self.min_follow_delay_hours)
        self.dt_unfollow_filter = instabotpatrik.filter.LastUnfollowFilter(
            more_than_hours_ago=self.min_unfollow_delay_hours)

        self.followed_by_count_filter = instabotpatrik.filter.UserFollowedByCountFilter(
            min_followed_by=self.min_count_followed_by,
            max_followed_by=self.max_count_followed_by)
        self.follows_count_filter = instabotpatrik.filter.UserFollowsCountFilter(min_follows=self.min_count_follows,
                                                                                 max_follows=self.max_count_follows)

        logging.info("[LFS] Workflow created. Like time filter")
        logging.info("[LFS] Using filter: min like delay: %d hours.", self.min_like_delay_hours)
        logging.info("[LFS] Using filter: min follow delay: %d hours.", self.min_follow_delay_hours)
        logging.info("[LFS] Using filter: min unfollow delay: %d hours.", self.min_unfollow_delay_hours)
        logging.info("[LFS] Using filter: Followed by count. Min: %d. Max: %d", self.min_count_followed_by,
                     self.max_count_followed_by)
        logging.info("[LFS] Using filter: Follows count. Min: %d. Max: %d", self.min_count_follows,
                     self.max_count_follows)

    def is_approved_for_lfs(self, user):
        return self.dt_follow_filter.passes(user) \
               and self.dt_unfollow_filter.passes(user) \
               and self.dt_like_filter.passes(user) \
               and self.followed_by_count_filter.passes(user) \
               and self.follows_count_filter.passes(user)

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
            self.media_controller.like(media_id=media_to_like.instagram_id, shortcode=media_to_like.shortcode)
            likes_given += 1

        logging.info("[LFS] Liking finished, let's follow him if we don't.")
        if media_owner.we_follow_user is False:
            self.user_controller.follow(instagram_id=media_owner.instagram_id)

        logging.info("[LFS] Finished. [user_id::%s username:%s] Gave %d likes.",
                     media_owner.instagram_id, media_owner.username, likes_given)


class UnfollowWorkflow:
    def __init__(self, user_controller):
        """
        :param user_controller:
        :type user_controller: instabotpatrik.core.UserController
        """
        self.user_controller = user_controller
        self.min_follow_delay_hours = 48
        logging.info("[LFS] Using filter: min follow delay = %d hours.", self.min_follow_delay_hours)
        self.dt_follow_filter = instabotpatrik.filter.LastFollowFilter(more_than_hours_ago=self.min_follow_delay_hours)

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
