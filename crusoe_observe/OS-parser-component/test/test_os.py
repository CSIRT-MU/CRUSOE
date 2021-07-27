from osrest.run import *

class TestOS():

    def test_time(self):
        expected = datetime(2018, 10, 10, 10, 10)
        tested = datetime(2018, 10, 10, 10, 14)
        rounded = round_time(tested)
        assert expected == rounded


