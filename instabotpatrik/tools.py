import time
import random


def get_time():
    return time.time()


def go_sleep(duration_sec, plusminus):
    time.sleep(duration_sec + plusminus * random.uniform(-1, 1))

