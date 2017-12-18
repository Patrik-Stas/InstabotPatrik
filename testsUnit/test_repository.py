from testsUnit.context import instabotpatrik
import unittest.mock
import datetime
import pytz


class TestConversionDatetimeToString(unittest.TestCase):
    def runTest(self):
        dt = datetime.datetime(2016, 8, 23, 17, 45, 15, tzinfo=pytz.UTC)
        dt_string = instabotpatrik.repository.datetime_to_db_format(dt)
        self.assertEquals(dt_string, "2016-08-23T17:45:15+00:00")


class ItShouldConvertDatetimeInDifferentTimezoneToStringInUTC(unittest.TestCase):
    def runTest(self):
        dt = datetime.datetime(2016, 8, 23, 17, 45, 15, tzinfo=pytz.timezone('CET'))
        dt_string = instabotpatrik.repository.datetime_to_db_format(dt)
        self.assertEquals(dt_string, "2016-08-23T16:45:15+00:00")


class ItShouldCreateOriginalDatetime(unittest.TestCase):
    def runTest(self):
        dt = datetime.datetime(2016, 8, 23, 17, 45, 15, tzinfo=pytz.timezone('UTC'))
        dt_string = instabotpatrik.repository.datetime_to_db_format(dt)
        dt_reparsed = instabotpatrik.repository.from_db_to_datetime(dt_string)
        self.assertEqual(dt.year, dt_reparsed.year)
        self.assertEqual(dt.month, dt_reparsed.month)
        self.assertEqual(dt.day, dt_reparsed.day)
        self.assertEqual(dt.hour, dt_reparsed.hour)
        self.assertEqual(dt.minute, dt_reparsed.minute)
        self.assertEqual(dt.second, dt_reparsed.second)


class ItShouldConvertIso8601UtcStringToDatetime(unittest.TestCase):

    def runTest(self):
        dt_string = "2016-08-23T17:45:15+00:00"
        dt = instabotpatrik.repository.from_db_to_datetime(dt_string)
        self.assertEquals(dt.tzname(), "UTC")
        self.assertEquals(dt.year, 2016)
        self.assertEquals(dt.month, 8)
        self.assertEquals(dt.day, 23)
        self.assertEquals(dt.hour, 17)
        self.assertEquals(dt.minute, 45)
        self.assertEquals(dt.second, 15)


class ItShouldConvertIso8601StringOutOfUtcToDatetime(unittest.TestCase):

    def runTest(self):
        dt_string = "2016-08-23T17:45:15+00:00"
        dt = instabotpatrik.repository.from_db_to_datetime(dt_string)
        self.assertEquals(dt.tzname(), "UTC")
        self.assertEquals(dt.hour, 17)


class ItShouldThrowExceptionIfTimezoneIsNotUTC(unittest.TestCase):

    def runTest(self):
        dt_string = "2016-08-23T17:45:15+01:00"
        self.assertRaises(instabotpatrik.repository.DataIntegrityException,
                          instabotpatrik.repository.from_db_to_datetime, dt_string)
