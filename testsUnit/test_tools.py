from testsUnit.context import instabotpatrik
import unittest
import time
import logging

logging.getLogger().setLevel(30)
logging.basicConfig(format='[%(levelname)s] [%(asctime)s] [%(name)s:%(funcName)s] : %(message)s',
                    datefmt='%m/%d/%Y-%H:%M:%S')


class ItShouldAllowActionAfterTimePasses(unittest.TestCase):
    def runTest(self):
        manager = instabotpatrik.tools.ActionManager()
        manager.allow_action_after_seconds("unfollow", 0.5)
        time.sleep(0.5)
        self.assertTrue(manager.is_action_allowed_now("unfollow"))


class ItShoulNotdAllowActionBeforeTimePasses(unittest.TestCase):
    def runTest(self):
        manager = instabotpatrik.tools.ActionManager()
        manager.allow_action_after_seconds("unfollow", 0.5)
        self.assertFalse(manager.is_action_allowed_now("unfollow"))


class ItShouldCalculateMinimalWaitingTime(unittest.TestCase):
    def runTest(self):
        manager = instabotpatrik.tools.ActionManager()
        manager.allow_action_after_seconds("liking_session", 10)
        manager.allow_action_after_seconds("unfollow", 20)
        time.sleep(0.8)
        self.assertEqual("liking_session", manager.seconds_left_until_some_action_possible()['action_name'])
        self.assertAlmostEqual(9, manager.seconds_left_until_some_action_possible()['sec_left'], delta=0.3)


class ItShouldReturnTimezoneAwareUTCDateTime(unittest.TestCase):
    def runTest(self):
        dt = instabotpatrik.tools.get_utc_datetime()
        self.assertEqual(dt.tzname(), "UTC")
