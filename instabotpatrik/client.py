import json
import sys
import time
import random
import logging

import instabotpatrik

if 'threading' in sys.modules:
    del sys.modules['threading']

logging.getLogger().setLevel(20)
logging.basicConfig(format='[%(levelname)s] [%(asctime)s] %(message)s', datefmt='%m/%d/%Y-%H:%M:%S')


class InstagramResponseException(Exception):
    def __init__(self, request_type, request_address, return_code):
        self.request_type = request_type
        self.request_address = request_address
        self.return_code = return_code


class InstagramClient:
    url = 'https://www.instagram.com/'

    url_user_detail = 'https://www.instagram.com/%s/?__a=1'  # %s = username

    url_follow = 'https://www.instagram.com/web/friendships/%s/follow/'  # %s = id of user
    url_unfollow = 'https://www.instagram.com/web/friendships/%s/unfollow/'  # %s = id of user

    url_tag = 'https://www.instagram.com/explore/tags/%s/?__a=1'  # %s = tag

    url_likes = 'https://www.instagram.com/web/likes/%s/like/'  # %s = id of media node
    url_unlike = 'https://www.instagram.com/web/likes/%s/unlike/'  # %s = id of media node

    url_media_detail = 'https://www.instagram.com/p/%s/?__a=1'  # %s = code of media node

    url_login = 'https://www.instagram.com/accounts/login/ajax/'
    url_logout = 'https://www.instagram.com/accounts/logout/'

    def __init__(self,
                 user_login,
                 user_password,
                 requests_session,
                 proxy=""):
        """

        :param user_login:
        :param user_password:
        :param requests_session:
        :type requests_session: requests.Session
        :param proxy:
        """
        self.s = requests_session
        self.proxy = proxy
        if proxy != "":
            proxies = {
                'http': 'http://' + proxy,
                'https': 'http://' + proxy,
            }
            self.s.proxies.update(proxies)
        # convert login to lower
        self.user_login = user_login.lower()
        self.user_password = user_password
        self._login_status = False
        self.ban_sleep_time_sec = 2 * 60 * 60  # If it seems like you'r banned - will sleep
        self.login_post = {
            'username': self.user_login,
            'password': self.user_password
        }
        self.csrftoken = None
        self.our_instagram_id = None

    @staticmethod
    def make_request(url, method_type, requests_callable):
        """
        :return: True if returned status code is 200-299. False otherwise
        :rtype: dict
        """
        logging.info("Sending [%s] %s", method_type, url)
        r = requests_callable(url)
        parsed_response = json.loads(r.text)
        logging.info("Response [%s] %s:\nStatus:%d", method_type, url, r.status_code)
        logging.debug("Response [%s] %s:\nBody:%s\n", method_type, url, json.dumps(parsed_response, indent=4))

        instabotpatrik.tools.go_sleep(3, 1)  # Let's make sure we don't send too many requests at once

        if 200 <= r.status_code < 300:
            return parsed_response
        else:
            raise InstagramResponseException("%s", url, r.status_code)

    def post_request(self, url):
        return self.make_request(url, "POST", self.s.post)

    def get_request(self, url):
        return self.make_request(url, "GET", self.s.get)

    def is_logged_in(self):
        return self._login_status

    def login(self):
        """
        :return: True if user was logged in, or login was succesfull. False otherwise
        :rtype: boolean
        """
        if self.is_logged_in():
            logging.info("Called login(), but already logged in.")
            return True
        self.s.cookies.update({
            'sessionid': '',
            'mid': '',
            'ig_pr': '1',
            'ig_vw': '1920',
            'csrftoken': '',
            's_network': '',
            'ds_user_id': ''
        })
        user_agent = ("Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/48.0.2564.103 Safari/537.36")
        self.s.headers.update({
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4',
            'Connection': 'keep-alive',
            'Content-Length': '0',
            'Host': 'www.instagram.com',
            'Origin': 'https://www.instagram.com',
            'Referer': 'https://www.instagram.com/',
            'User-Agent': user_agent,
            'X-Instagram-AJAX': '1',
            'X-Requested-With': 'XMLHttpRequest'
        })
        r = self.s.get(self.url)
        self.s.headers.update({'X-CSRFToken': r.cookies['csrftoken']})
        time.sleep(2 + 3 * random.random())
        login = self.s.post(self.url_login, data=self.login_post, allow_redirects=True)
        self.s.headers.update({'X-CSRFToken': login.cookies['csrftoken']})
        self.csrftoken = login.cookies['csrftoken']
        time.sleep(2 + 3 * random.random())

        if login.status_code == 200:
            r = self.s.get('https://www.instagram.com/')
            finder = r.text.find(self.user_login)
            if finder != -1:
                self.our_instagram_id = self.get_user_with_details(self.user_login)
                self._login_status = True
                logging.info('%s login success!', self.user_login)
                return True
            else:
                self._login_status = False
                logging.error('Login error! Check your login data!')
        else:
            logging.error('Login error! Connection error!')
        return False

    def logout(self):
        """
        :return: was logout successful
        :rtype: boolean
        """
        logging.info('Logout.')
        try:
            logout_post = {'csrfmiddlewaretoken': self.csrftoken}
            self.s.post(self.url_logout, data=logout_post)
            logging.info("Logout success!")
            self._login_status = False
            self.s.close()
            return True
        except Exception as e:
            logging.error(e, exc_info=True)
            return False

    def get_latest_media_by_tag(self, tag):
        """
        :param tag:
        :return: list of most recently posted media containing specified tag
        :rtype: list of instabotpatrik.model.InstagramMedia
        """
        try:
            r_object = self.get_request(self.url_tag % tag)
            media_dict = list(r_object['tag']['media']['nodes'])
            media_objs = []
            for node in media_dict:
                node_obj = instabotpatrik.model.InstagramMedia(instagram_id=node['id'],
                                                               shortcode=node['code'],
                                                               owner_id=node['owner']['id'],
                                                               like_count=node['likes']['count'],
                                                               caption=node['caption'])
                media_objs.append(node_obj)

            return media_objs
        except Exception as e:
            logging.error(e, exc_info=True)
            return None

    # GET MEDIA BY TAG response:
    # { tag
    #   { media
    #       { nodes
    #           [ {
    #               comments_disabled: false,
    #               id: "1656645974179003456",
    #               owner: { id: "30554066" },
    #               thumbnail_src: "https://something.jpg",
    #               thumbnail_resources: [ ... ],
    #               is_video: false,
    #               code: "Bb9lrx5hTxA",
    #               date: 1511707611,
    #               display_src: "https//:url.jpg",
    #               caption: "Cathedrale Saint-Guy  #prague #cathedral #travel",
    #               comments: { count: 0  },
    #               likes: { count: 3 }
    #             },
    #             ...
    #            ]
    #       }
    #   }
    # }

    def get_user_with_details(self, username):
        """
        :rtype: instabotpatrik.model.InstagramUser
        """
        try:
            r_object = self.get_request(self.url_user_detail % username)
            user_info = r_object['user']
            detail = instabotpatrik.model.InstagramUserDetail(url=user_info['external_url'],
                                                              count_shared_media=user_info['media']['count'],
                                                              count_follows=user_info['follows']['count'],
                                                              count_followed_by=user_info['followed_by']['count'],
                                                              we_follow_user=user_info['followed_by_viewer'],
                                                              user_follows_us=user_info['follows_viewer'])
            return instabotpatrik.model.InstagramUser(instagram_id=user_info['id'],
                                                      username=user_info['username'],
                                                      user_detail=detail)

        except Exception as e:
            logging.error(e, exc_info=True)
            return None
            # user: {
            #           biography: "profile description text"
            #           country_block: false,
            #           external_url: "http://www.patrikstas.com/",
            #           external_url_linkshimmed: "ref to external_url via instagram redirection"
            #           followed_by: { count: 196 },
            #           followed_by_viewer: false,
            #           follows: { count: 228 },
            #           follows_viewer: true,
            #           full_name: "Patrik Stas",
            #           has_blocked_viewer: false,
            #           has_requested_viewer: false,
            #           id: "508389516",
            #           is_private: false,
            #           is_verified: false,
            #           profile_pic_url: "https://instagram.f6430609_a.jpg",
            #           profile_pic_url_hd: "https://instagram.f0sadas9_a.jpg",
            #           requested_by_viewer: false,
            #           username: "patrikstas",
            #           connected_fb_page: null,
            #           media: {
            #               nodes: [  {}, {} ],
            #               count: 67,
            #               page_info: {
            #                   has_next_page: true,
            #                   end_cursor: "come_code_4k2j4b32j4b23b2j34"
            #               }
            #           },
            #           saved_media: {
            #               nodes: [],
            #               count: 0,
            #               page_info: {
            #                   has_next_page: false,
            #                   end_cursor: null
            #               }
            #           }
            #       },
            # logging_page_id: "profilePage_508389516"
            # }

    def get_media_detail(self, shortcode_media):
        """
        :param shortcode_media:
        :return: media details
        :rtype: instabotpatrik.model.InstagramMedia
        """
        try:
            r_object = self.get_request(self.url_media_detail % shortcode_media)
            shortcode_media = r_object['graphql']['shortcode_media']
            return instabotpatrik.model.InstagramMedia(instagram_id=shortcode_media['id'],
                                                       shortcode=shortcode_media['shortcode'],
                                                       owner_id=shortcode_media['owner']['id'],
                                                       owner_username=shortcode_media['owner']['username'],
                                                       caption=shortcode_media['edge_media_to_caption']
                                                       ['edges'][0]['node']['text'],
                                                       is_liked=shortcode_media['viewer_has_liked'],
                                                       like_count=shortcode_media['edge_media_preview_like']['count'])
        except Exception as e:
            logging.error(e, exc_info=True)
            return None

    # {
    #     graphql: {
    #         shortcode_media: {
    #             __typename: "GraphImage",
    #             id: "16105704222123123",
    #             shortcode: "BcIxwI8KDKA",
    #             dimensions: {...},
    #             is_video: false,
    #             edge_media_to_caption: {
    #                 edges: [
    #                     {
    #                         node: {
    #                             text: "description text "
    #                         }
    #                     }
    #                 ]
    #             },
    #             caption_is_edited: false,
    #             edge_media_to_comment: {
    #                 count: 3,
    #                 page_info: {
    #                     has_next_page: false,
    #                     end_cursor: null
    #                 },
    #                 edges: [ ... comments ... ]
    #             }
    #             edge_media_preview_like: {
    #                     count: 43,
    #                     edges: [ ... likes ... ]
    #             }
    #             location: {...},
    #             viewer_has_liked: true,
    #             viewer_has_saved: false,
    #             viewer_has_saved_to_collection: false,
    #             owner: {
    #                 id: "284740851",
    #                 username: "_filipchudoba",
    #                 blocked_by_viewer: false,
    #                 followed_by_viewer: false,
    #                 full_name: "Filip Chudoba",
    #                 has_blocked_viewer: false,
    #                 is_private: false,
    #                 is_unpublished: false,
    #                 is_verified: false,
    #                 requested_by_viewer: false
    #             }
    #         }
    #     }
    # }

    def like(self, media_id):
        """
        :param media_id:
        :return: True if giving like was successfull
        :rtype: bool
        """
        try:
            r_object = self.post_request(self.url_likes % media_id)
            return True if r_object['status'] == 'ok' else False
        except InstagramResponseException as e:
            logging.error(e, exc_info=True)
            logging.error("Unsatisfying response from Instagram. Sleep %d seconds now.", self.ban_sleep_time_sec)
            time.sleep(self.ban_sleep_time_sec)
            return False

    def follow(self, user_id):
        """
        :param user_id:
        :return: True if giving follow was successfull
        :rtype: bool
        """
        try:
            r_object = self.post_request(self.url_follow % user_id)
            return True if r_object['status'] == 'ok' else False
        except InstagramResponseException as e:
            logging.error(e, exc_info=True)
            logging.error("Unsatisfying response from Instagram. Sleep %d seconds now.", self.ban_sleep_time_sec)
            time.sleep(self.ban_sleep_time_sec)
            return False

    def unfollow(self, user_id):
        """
        :param user_id:
        :return: True if giving follow was successfull
        :rtype: bool
        """
        try:
            r_object = self.post_request(self.url_unfollow % user_id)
            return True if r_object['status'] == 'ok' else False
        except InstagramResponseException as e:
            logging.error(e, exc_info=True)
            logging.error("Unsatisfying response from Instagram. Sleep %d seconds now.", self.ban_sleep_time_sec)
            time.sleep(self.ban_sleep_time_sec)
            return False
