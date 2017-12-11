import time
import random
import logging

logging.getLogger().setLevel(20)
logging.basicConfig(format='[%(levelname)s] [%(asctime)s] %(message)s', datefmt='%m/%d/%Y-%H:%M:%S')


class UnknownActionException:
    def __init__(self, unknown_action):
        self.unknown_action = unknown_action
        # TODO: Pass the message to the exception text or smtng


def get_time():
    return time.time()


def go_sleep(duration_sec, plusminus):
    logging.info("Going to sleep for about %d", duration_sec)
    time.sleep(duration_sec + (plusminus * random.uniform(-1, 1)))


class ActionManager:

    def __init__(self):
        self.allowed_actions = ["like", "follow", "unfollow"]
        self.actions_timestamps = {}

    def action_limit_was_registered(self, action):
        return action in self.actions_timestamps.keys()

    def is_action_allowed_now(self, action_name):
        if action_name in self.allowed_actions:
            if action_name in self.actions_timestamps.keys():
                allowed = time.time() >= self.actions_timestamps[action_name]
                if not allowed:
                    logging.info("Action '%s' not allowed now. Will be possible after %f seconds", action_name,
                                 self.time_left_until_action_possible(action_name))
            else:
                return True
        else:
            raise UnknownActionException(action_name)

    def allow_action_after_seconds(self, action_name, seconds):
        if action_name in self.allowed_actions:
            self.actions_timestamps[action_name] = time.time() + seconds
        else:
            raise UnknownActionException(action_name)

    def time_left_until_action_possible(self, action_name):
        if action_name in self.allowed_actions:
            if not self.action_limit_was_registered(action_name):
                return 0
            else:
                left_seconds = self.actions_timestamps[action_name] - time.time()
                return 0 if 0 >= left_seconds else left_seconds
        else:
            raise UnknownActionException(action_name)

    def time_left_until_some_action_possible(self):
        if len(self.actions_timestamps.keys()) == 0:
            return {"sec_left": 0, "action_name": None}

        min_sec_left = 1000000.0
        min_action_name = None
        for action_name, timestamp in self.actions_timestamps.items():
            action_sec_left = self.time_left_until_action_possible(action_name)
            if action_sec_left < min_sec_left:
                min_sec_left = action_sec_left
                min_action_name = action_name
        return {"sec_left": min_sec_left, "action_name": min_action_name}
