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
        return time.time() > self.actions_timestamps[action_name]

    def allow_action_after_seconds(self, action_name, seconds):
        self.actions_timestamps[action_name] = time.time() + seconds
