import unittest
from datetime import datetime as dt
from math import ceil

from ztm_buses.modules.Bus import Bus
from ztm_buses.modules.Coordinates import Coordinates



class BusTest(unittest.TestCase):
    def __setup(self) -> None:
        # set up
        self.bus = Bus.Bus("1111")

    def __test_update(self):
        # test_update()
        coor1 = Coordinates(20.912840492412776, 52.1746492871965)
        coor2 = Coordinates(20.913248188164914, 52.175576991168214)
        coor3 = Coordinates(20.913645155084335, 52.17662968147784)
        coor4 = Coordinates(20.91439617358658, 52.17880077658759)
        coor5 = Coordinates(20.917067653723922, 52.18636588590337)

        def time_formater(x: str):
            return dt.strptime(x, '%Y-%m-%d %H:%M:%S')

        times = ["2024-04-01 12:10:00", "2024-04-01 12:10:10", "2024-04-01 12:10:10",
                 "2024-04-01 12:10:20", "2024-04-01 12:10:20", "2024-04-01 12:10:30",
                 "2024-04-01 12:10:40", "2024-04-01 12:10:50"]
        times = list(map(time_formater, times))

        my_lines = ["121", "121", "121", "121", "122", "122", "122", "122"]
        my_brigades = ["01", "", "01", "01", "01", "02", "02", ""]

        my_coord = [coor1, coor2, coor2, coor3, coor4, coor4, coor5, coor5]

        for i in range(len(times)):
            self.bus.update(my_lines[i], my_brigades[i],
                            my_coord[i].lon, my_coord[i].lat, times[i])

        states = self.bus.get_all_states()
        lines = self.bus.get_all_lines()
        brigades = self.bus.get_all_brigades()
        self.assertEqual(len(states), 6)
        self.assertEqual(len(lines),  6)
        self.assertEqual(len(brigades), 6)

        # we have this treshhold becase coord.lon returns in degrees so we do 2 times
        # conversion rad - deg hence the floating numbers do not agree
        treshhold = 1e-8
        assert(states[0][0] == times[0] and states[0][1] - my_coord[0] < treshhold)
        assert(states[1][0] == times[1] and states[1][1] - my_coord[1] < treshhold)
        assert(states[2][0] == times[3] and states[2][1] - my_coord[3] < treshhold)
        assert(states[3][0] == times[5] and states[3][1] - my_coord[5] < treshhold)
        assert(states[4][0] == times[6] and states[4][1] - my_coord[6] < treshhold)
        assert(states[5][0] == times[7] and states[5][1] - my_coord[7] < treshhold)
        assert(lines[1] == "121" and brigades[1] == "01")

    def __test_speed_compute(self):
        # test speed computation

        self.__setup()
        self.__test_update()
        # distance between coordinates from the previous test
        distance12 = 107.23
        distance23 = 116.09
        distance34 = 254.4
        distance45 = 859.67

        error = 0.05
        def lower(x): return x - error*x
        def upper(x): return x + error*x
        def helper(x, y): return lower(x) < y < upper(x)

        # we do ceiling in Bus.speed_compute so it is fair
        def speed_helper(x): return ceil(3.6 * x/10)
        speeds = self.bus.speed_compute()
        assert(helper(speed_helper(distance12), speeds[0][0]))
        assert(helper(speed_helper(distance23), speeds[1][0]))
        assert(helper(speed_helper(distance34), speeds[2][0]))
        assert(helper(speed_helper(distance45), speeds[3][0]))
        self.assertEqual(0, speeds[4][0])


if __name__ == "__main__":
    unittest.main()
