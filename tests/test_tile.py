import unittest
from backend.tile import Tile


class TestTile(unittest.TestCase):
    def setUp(self):
        self.tile = Tile()

    def test_place_mine(self):
        self.assertTrue(not self.tile.is_mine())
        self.tile.place_mine()
        self.assertTrue(self.tile.is_mine())

    def test_mark_as_revealed(self):
        self.assertTrue(not self.tile.is_revealed())
        self.tile.mark_as_revealed()
        self.assertTrue(self.tile.is_revealed())

    def test_flag_tile(self):
        self.assertTrue(not self.tile.is_revealed())
        self.tile.place_flag()
        self.assertTrue(self.tile.is_flagged())
        self.tile.remove_flag()
        self.assertTrue(not self.tile.is_flagged())
        self.tile.mark_as_revealed()
        self.assertTrue(self.tile.is_revealed())
        with self.assertRaises(Exception):
            self.tile.place_flag()
