# -*- coding: utf-8 -*-
# from unittest.mock import MagicMock
# from unittest.mock import PropertyMock
# from unittest.mock import Mock
from testsUnit.context import instabotpatrik
import unittest
import unittest.mock


def my_side_effect(*args, **kwargs):
    # print("Inside mock args:   %s", str(args))
    # print("Inside mock kwargs: %s", str(kwargs))
    # if 0 < args[0] < 100:
    #     print("MOCK CHECK: range is OK")

    if kwargs['type'] == "double":
        return args[0] * 20
    elif kwargs['type'] == "triple":
        return args[0] * 30
    else:
        raise Exception("Mock: Operation not supported")


class ItShouldTestSample(unittest.TestCase):
    def test_run(self):
        mymock = unittest.mock.create_autospec(instabotpatrik.sample.MyModifier)
        mymock.modify.side_effect = my_side_effect
        mymock.modify(2, type="double")


if __name__ == '__main__':
    unittest.main()
