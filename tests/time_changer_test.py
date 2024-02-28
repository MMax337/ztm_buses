import unittest
from datetime import datetime
from ztm_buses.modules.time_changer import time_changer



class TimeChangerTest(unittest.TestCase):
    def test_time_changer(self):
        time1 = "2024-04-01 00:00:00"
        time2 = "2024-04-01 13:59:31"
        time3 = "2024-04-01 28:42:45"
        time4 = "2024-04-01 50:78:61"

        result1 = time_changer(time1)
        result2 = time_changer(time2)
        result3 = time_changer(time3)
        result4 = time_changer(time4)

        self.assertEqual(result1, datetime(2024, 4, 1, 0, 0, 0))
        self.assertEqual(result2, datetime(2024, 4, 1, 13, 59, 31))
        self.assertEqual(result3, datetime(2024, 4, 2, 4, 42, 45))
        self.assertEqual(result4, datetime(2024, 4, 3, 3, 19, 1))


if __name__ == '__main__':
    unittest.main()
