import time
import random
import os


def get_time():
    return time.time()


def go_sleep(duration_sec, plusminus):
    time.sleep(duration_sec + plusminus * random.uniform(-1, 1))


def get_path_to_file_in_directory_of_this_file(file_name):
    this_directory_absolute = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    return os.path.join(this_directory_absolute, file_name)
