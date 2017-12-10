import time
import random


def get_time():
    return time.time()


def go_sleep(duration_sec, plusminus):
    time.sleep(duration_sec + plusminus * random.uniform(-1, 1))


class ActionManager:

    def __init__(self):
        self.actions_timestamps = {}

    def is_action_allowed_now(self, action_name):
        return time.time() >= self.actions_timestamps[action_name]

    def allow_action_after_seconds(self, action_name, seconds):
        self.actions_timestamps[action_name] = time.time() + seconds

    def _time_left_until_action_possible(self, action_name):
        left_seconds = self.actions_timestamps[action_name] - time.time()
        return 0 if 0 >= left_seconds else left_seconds

    def time_left_until_some_action_possible(self):
        min_sec_left = 1000000.0
        for action_name, timestamp in self.actions_timestamps.items():
            action_sec_left = self._time_left_until_action_possible(action_name)
            min_sec_left = action_sec_left if action_sec_left < min_sec_left else min_sec_left
        return min_sec_left
