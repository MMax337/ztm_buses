import unittest

from ztm_buses.modules.Coordinates import Coordinates


class CoordinatesTest(unittest.TestCase):

    def test_distance(self):
        error = 0.05
        def lower(x): return x - error*x
        def upper(x): return x + error*x
        def helper(x, y): return lower(x) < y < upper(x)
        coor1 = Coordinates(20.912840492412776, 52.1746492871965)
        coor2 = Coordinates(20.913248188164914, 52.175576991168214)
        coor3 = Coordinates(20.913645155084335, 52.17662968147784)
        coor4 = Coordinates(20.91439617358658, 52.17880077658759)
        coor5 = Coordinates(20.917067653723922, 52.18636588590337)
        # distances calculated by google maps
        distance12 = 107.23
        distance23 = 116.09
        distance34 = 254.4
        distance45 = 859.67

        assert (helper(distance12, coor1 - coor2))
        assert (helper(distance23, coor2 - coor3))
        assert (helper(distance34, coor3 - coor4))
        assert (helper(distance45, coor4 - coor5))


if __name__ == '__main__':
    unittest.main()
