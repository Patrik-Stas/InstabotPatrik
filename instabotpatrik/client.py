import json
import sys
import time
import random
import logging
import requests
import os
import pickle

import instabotpatrik

if 'threading' in sys.modules:
    del sys.modules['threading']


class InstagramResponseException(Exception):
    def __init__(self, request_type, request_address, return_code):
        self.request_type = request_type
        self.request_address = request_address
        self.return_code = return_code


class InstagramLoginException(Exception):
    def __init__(self, reason):
        self.reason = reason


# TODO : Need to wrap mappings with try/except and raise some sort of mapping/parsing exceptions ... for example
# when we try to use some field in Instagram response which doesn't exist (might be optional)

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
                 proxy="",
                 try_to_load_session_from_file=False):
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
        self.try_to_load_session_from_file = try_to_load_session_from_file
        self.our_user = None

    def pretty_print(self, req):
        """
        At this point it is completely built and ready
        to be fired; it is "prepared".

        However pay attention at the formatting used in
        this function because it is programmed to be pretty
        printed and may differ from the actual request.
        """
        logging.debug('{}\n{}\n{}\n\n{}'.format(
            '-----------START-----------',
            req.method + ' ' + req.url,
            '\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
            req.body,
        ))

    def make_request(self, url, method_type, callable):
        """
        :return: True if returned status code is 200-299. False otherwise
        :rtype: dict
        """
        instabotpatrik.tools.go_sleep(6, plusminus=3)  # Let's make sure we don't send too many requests at once
        # request = requests.Request(method_type, url)
        # prepared_request = self.s.prepare_request(request)
        # logging.info("[CLIENT] Sending [%s] %s", method_type, url)
        # self.pretty_print(prepared_request)
        # r = self.s.send(prepared_request)
        # logging.info("[CLIENT] Response [%s] %s:\nStatus:%d", method_type, url, r.status_code)
        logging.info("Going to send [%s] %s", method_type, url)
        r = callable(url)  # TODO figure out how to log request headers, if I use method above, mocking in tests is hard
        if 200 <= r.status_code < 300:
            logging.info("Response seems good. Response status code: %d", r.status_code)
            parsed_response = None
            if r.text is not None:
                parsed_response = json.loads(r.text)
                logging.debug("[CLIENT] Response [%s] %s:\nBody:%s\n", method_type, url,
                              json.dumps(parsed_response, indent=4))
            return parsed_response
        else:
            logging.error("Instagram doesn't like us. Response status code %d", r.status_code)
            raise InstagramResponseException(method_type, url, r.status_code)

    def post_request(self, url):
        return self.make_request(url, "POST", self.s.post)

    def get_request(self, url):
        return self.make_request(url, "GET", self.s.get)

    def is_logged_in(self):
        logging.info("Verifying whether we are logged in ... ")
        time.sleep(2 + 3 * random.random())
        r = self.s.get('https://www.instagram.com/')
        finder = r.text.find(self.user_login)
        if finder != -1:
            return True
        else:
            logging.debug("[CLIENT] You don't seem to be logged in, Instagram responded: \n%s", r.text)
            logging.info("[CLIENT] You don't seem to be logged in, the response code is:%d ", r.status_code)
            return False

    #
    # def asure_basic_cookies_for_session(self):
    #     self.s.cookies.update({
    #         'sessionid': '',
    #         'mid': '',
    #         'ig_pr': '1',
    #         'ig_vw': '1920',
    #         'csrftoken': '',
    #         's_network': '',
    #         'ds_user_id': ''
    #     })

    def asure_basic_headers_for_session(self):
        self.s.headers.update({
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4',
            'Connection': 'keep-alive',
            'Content-Length': '0',
            'Host': 'www.instagram.com',
            'Origin': 'https://www.instagram.com',
            'Referer': 'https://www.instagram.com/',
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36",
            'X-Instagram-AJAX': '1',
            'X-Requested-With': 'XMLHttpRequest'
        })

    def _update_csfr_header(self, csfr_token):
        logging.info("Updating session headers with CSFR token:%s", csfr_token)
        self.csfr_token = csfr_token
        self.s.headers.update({'X-CSRFToken': self.csfr_token})

    def _get_cookies_filename(self):
        return '%s.cookies.bin' % self.user_login

    # def _get_headers_filename(self):
    #     return '%s.headers.json' % self.user_login

    def persist_cookies_for_user(self):
        logging.info("Saving session cookies to file %s" % self._get_cookies_filename())
        # If we save the cookie dictionary, we loose information about to which host and path these cookies belong.
        # Then if you load them and update requests session with it, it will use these cookies
        # for every host on its root path "/"
        # with open(self._get_cookies_filename(), 'w') as f:
        #     dict_cookie = requests.utils.dict_from_cookiejar(self.s.cookies)
        #     json.dump(dict_cookie, f)
        with open(self._get_cookies_filename(), 'wb') as f:
            pickle.dump(self.s.cookies, f)

    # def persist_headers_for_user(self):
    #     logging.info("Saving session headers to file %s" % self._get_headers_filename())
    #     with open(self._get_headers_filename(), 'w') as f:
    #         json.dump(self.s.headers, f)

    def load_cookies_from_file_for_user(self):
        # with open(self._get_cookies_filename(), 'r') as f:
        #     loaded_cookie_dict = json.load(f)
        #     loaded_cookiejar = requests.utils.cookiejar_from_dict(loaded_cookie_dict)
        #     # for k in loaded_cookiejar.iterkeys():
        #     #     self.s.cookies[k] = loaded_cookiejar[k]
        #     self.s.cookies.update(loaded_cookiejar)
        #     # loaded_cookie_dict, or loaded_cookiejar, they don't have information about host. You would have to
        #     # dig into the jar and set it up yourself before you start updating your session's cookies
        #     # self.s.cookies = cookiejar
        with open(self._get_cookies_filename(), 'rb') as f:
            cookies_with_host = pickle.load(f)
            self.s.cookies.update(cookies_with_host)

    def is_cookie_file_for_user_available(self):
        expected_cookie_file = self._get_cookies_filename()
        return os.path.isfile(expected_cookie_file)

    def _try_load_session_for_user_from_file(self):
        if self.is_cookie_file_for_user_available():
            logging.info("Cookie file %s was found. Will load session for user from file.",
                         self._get_cookies_filename())
            self.load_cookies_from_file_for_user()
            assert self.s.cookies['csrftoken'] is not None
            self._update_csfr_header(self.s.cookies['csrftoken'])
            return True
        else:
            logging.info("Cookie file %s was not found. Will not load session for user from file.",
                         self._get_cookies_filename())
            return False

    def _execute_fresh_login_procedure(self):
        logging.info("[CLIENT] Going to do new login. Sending first request to Instagram.")

        # self.asure_basic_cookies_for_session()
        self.asure_basic_headers_for_session()
        instagram_response = self.s.get(self.url)
        self._update_csfr_header(instagram_response.cookies['csrftoken'])  # get csfr while still not logged in
        time.sleep(4 + 3 * random.random())  # time for entering password...
        login_data = {
            'username': self.user_login,
            'password': self.user_password
        }
        logging.info("[CLIENT] Now going to send login request with credentials.")
        login_response = self.s.post(self.url_login, data=login_data, allow_redirects=True)  # try login
        logging.info("[CLIENT] The request to login with credentials received response with body:\n%s",
                     login_response.text)
        logging.info("[CLIENT] The request to login with credentials received status code: %s",
                     login_response.status_code)
        logging.info("[CLIENT] Received new CSFR token %s", self.csfr_token)

        parsed_response = json.loads(login_response.text)
        if login_response.status_code != 200 or parsed_response['authenticated'] is not True:
            raise InstagramLoginException("Failed login. We send credentials and received back code %d. Body:%s" %
                                          (login_response.status_code, login_response.text))
        self._update_csfr_header(login_response.cookies['csrftoken'])

    def login(self):
        """
        :return: True if user was logged in, or login was succesfull. False otherwise
        :rtype: boolean
        """
        logging.info("Running first check to see if we are already logged in.")
        if self.is_logged_in():
            logging.info("[CLIENT] Called login(), but already logged in.")
            return True
        else:
            logging.warning("[CLIENT] Seem like we are not logged in yet. I am going to proceed with login.")

        logging.info("Should we load session from file?")
        if self.try_to_load_session_from_file:
            logging.info("[CLIENT] Try load session from file is enabled. Will try.")
            success = self._try_load_session_for_user_from_file()
            self.asure_basic_headers_for_session()
            if success:
                if self.is_logged_in():
                    logging.info("[CLIENT] Session was loaded from file and accessing Instagram was verified.")
                    return True
                else:
                    logging.warning("[CLIENT] Session was loaded from file but seems like we are not "
                                    "really logged in instagram")
        else:
            logging.info("We are not gonna try load session from file.")

        self._execute_fresh_login_procedure()

        logging.info("[CLIENT] Sleeping for few seconds, then we will verify that we are logged in.")
        time.sleep(3 + 3 * random.random())
        logging.info("[CLIENT] Going to verify that we are really logged in.")

        if self.is_logged_in():
            our_user = self.get_our_user()
            logging.info('[CLIENT] Success! We are logged in under instagram_id:%s/username:%s!',
                         our_user.instagram_id, our_user.username)
            self.persist_cookies_for_user()
            # self.persist_headers_for_user()
            #  ->>> TypeError: Object of type 'CaseInsensitiveDict' is not JSON serializable
            return True
        else:
            raise InstagramLoginException("[CLIENT] We failed logging into Instagram :(")

    def get_our_user(self):
        if self.our_user is None:
            self.our_user = self.get_user_with_details(self.user_login)
        return self.our_user

    def logout(self):
        """
        :return: was logout successful
        :rtype: boolean
        """
        logging.info('Logout.')
        try:
            logout_post = {'csrfmiddlewaretoken': self.csfr_token}
            self.s.post(self.url_logout, data=logout_post)
            logging.info("[CLIENT] Logout success!")
            self._login_status = False
            self.s.close()
            return True
        except Exception as e:
            logging.error(e, exc_info=True)
            return False

    @staticmethod
    def _parse_media_nodes(media_nodes):
        media_objs = []
        for node in media_nodes:
            node_obj = instabotpatrik.model.InstagramMedia(instagram_id=node['id'],
                                                           shortcode=node['code'],
                                                           owner_id=node['owner']['id'],
                                                           like_count=node['likes']['count'],
                                                           caption=node['caption'] if 'caption' in node else "")
            media_objs.append(node_obj)

        return media_objs

    def get_recent_media_by_tag(self, tag):
        """
        :param tag:
        :return: list of most recently posted media containing specified tag
        :rtype: list of instabotpatrik.model.InstagramMedia
        """
        r_object = self.get_request(self.url_tag % tag)
        media_dict = list(r_object['tag']['media']['nodes'])
        return self._parse_media_nodes(media_dict)

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

    def get_recent_media_of_user(self, username):
        """
        :param username:
        :return:
        :rtype: list of instabotpatrik.model.InstagramMedia
        """
        r_object = self.get_request(self.url_user_detail % username)
        dict_medias = list(r_object['user']['media']['nodes'])
        medias = []
        for dict_media in dict_medias:
            recent_media = instabotpatrik.model.InstagramMedia(instagram_id=dict_media['id'],
                                                               shortcode=dict_media['code'],
                                                               owner_id=dict_media['owner']['id'],
                                                               owner_username=username,
                                                               caption=dict_media['caption'] if dict_media[
                                                                   'caption'] else None,
                                                               like_count=dict_media['likes']['count'])
            medias.append(recent_media)
        return medias

    def get_media_detail(self, shortcode_media):
        """
        :param shortcode_media:
        :return: media details
        :rtype: instabotpatrik.model.InstagramMedia
        """
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

    def get_user_with_details(self, username):
        """
        :rtype: instabotpatrik.model.InstagramUser
        """
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

    def like(self, media_id):
        """
        :param media_id:
        :return: True if giving like was successfull
        :rtype: bool
        """
        r_object = self.post_request(self.url_likes % media_id)
        return True if r_object['status'] == 'ok' else False

    def follow(self, user_id):
        """
        :param user_id:
        :return: True if giving follow was successfull
        :rtype: bool
        """
        r_object = self.post_request(self.url_follow % user_id)
        return True if r_object['status'] == 'ok' else False

    def unfollow(self, user_id):
        """
        :param user_id:
        :return: True if giving follow was successfull
        :rtype: bool
        """
        r_object = self.post_request(self.url_unfollow % user_id)
        return True if r_object['status'] == 'ok' else False
