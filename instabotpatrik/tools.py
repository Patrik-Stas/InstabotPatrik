import random
import logging
import pytz
import datetime
import time


class UnknownActionException:
    def __init__(self, unknown_action):
        self.unknown_action = unknown_action
        # TODO: Pass the message to the exception text or smtng


def get_utc_datetime():
    """
    :rtype datetime.datetime
    :return:
    """
    return datetime.datetime.now(tz=pytz.UTC)



def go_sleep(duration_sec, plusminus):
    sleep_duration = duration_sec if plusminus < 0.01 else duration_sec + (plusminus * random.uniform(-1, 1))
    logging.info("Going to sleep for %f seconds", sleep_duration)
    time.sleep(sleep_duration)


class ActionManager:

    def __init__(self):
        self.allowed_actions = ["unfollow", "liking_session"]
        self.actions_timestamps = {}

    def action_limit_was_registered(self, action):
        return action in self.actions_timestamps.keys()

    def is_action_allowed_now(self, action_name):
        if action_name in self.allowed_actions:
            if action_name in self.actions_timestamps.keys():
                allowed = get_utc_datetime() >= self.actions_timestamps[action_name]
                if not allowed:
                    logging.info("Action '%s' not allowed now. Will be possible after %f seconds", action_name,
                                 self.seconds_left_until_action_possible(action_name))
                return allowed
            else:
                return True
        else:
            raise UnknownActionException(action_name)

    def allow_action_after_seconds(self, action_name, seconds):
        logging.info("Will allow %s after %d seconds", action_name, seconds)
        if action_name in self.allowed_actions:
            self.actions_timestamps[action_name] = get_utc_datetime() + datetime.timedelta(seconds=seconds)
        else:
            raise UnknownActionException(action_name)

    def seconds_left_until_action_possible(self, action_name):
        if action_name in self.allowed_actions:
            if not self.action_limit_was_registered(action_name):
                return 0
            else:
                now = get_utc_datetime()
                allowed_time = self.actions_timestamps[action_name]
                return 0 if now >= allowed_time else (allowed_time - now).seconds
        else:
            raise UnknownActionException(action_name)

    def seconds_left_until_some_action_possible(self):
        if len(self.actions_timestamps.keys()) == 0:
            return {"sec_left": 0, "action_name": None}

        min_sec_left = 1000000.0
        min_action_name = None
        for action in self.allowed_actions:
            action_sec_left = self.seconds_left_until_action_possible(action)
            if action_sec_left < min_sec_left:
                min_sec_left = action_sec_left
                min_action_name = action
        return {"sec_left": min_sec_left, "action_name": min_action_name}
