import math
import random
from os import urandom
from typing import List, Tuple
from backend.tile import Tile


class Grid:
    """
    There are 2 grids: _tile_grid and _mine_count_grid grid.

    Both are dicts and values are accessed by key in a form of tuple (row, column) where both
        of those are integers and represent index. So minimum for both is 0 and maximum is grid_size-1

    _tile_grid has Tile() object for values while _mine_count_grid has integers which represent bomb count
    around that location.
    """

    # Possible directions (relative to the current (row, column) index value)
    ROTATIONS = [(-1, -1), (-1,  0), (-1,  1),
                 ( 0, -1),           ( 0,  1),
                 ( 1, -1), ( 1,  0), ( 1,  1)]

    def __init__(self, grid_height: int, grid_width: int, mine_count: int, *, seed: int = None):
        Grid.check_valid_grid_arguments(grid_height, grid_width, mine_count)
        self._grid_height = grid_height
        self._grid_width = grid_width
        self._mine_count = mine_count
        self._tile_grid = {}
        self._mine_count_grid = {}
        self.seed = seed if seed is not None else Grid.generate_seed()
        random.seed(seed)
        self._set_up_grid()

    def __str__(self):
        visualization = []
        for row in range(self._grid_height):
            for col in range(self._grid_width):
                if self._tile_grid[row, col].is_revealed() and self._mine_count_grid[row, col] > 0:
                    visualization.append(str(self._mine_count_grid[row, col]))
                else:
                    visualization.append(str(self._tile_grid[row, col]))
            visualization.append("\n")
        return " ".join(visualization)

    def get_area_size(self) -> int:
        return self._grid_height * self._grid_width

    def get_grid_height(self) -> int:
        return self._grid_height

    def get_grid_width(self) -> int:
        return self._grid_width

    def get_mine_count(self) -> int:
        return self._mine_count

    def get_minimum_recommended_mines(self) -> int:
        return math.ceil(self.get_area_size() * 0.1)

    def get_maximum_recommended_mines(self) -> int:
        return math.ceil(self.get_area_size() * 0.5)

    def get_tile(self, row: int, col: int) -> Tile:
        return self._tile_grid[row, col]

    def get_surrounding_mine_count(self, row: int, col: int) -> int:
        return self._mine_count_grid[row, col]

    def is_tile_empty(self, row: int, col: int) -> bool:
        """
        Empty tile represent tile that doesn't have a bomb and isn't a indicator (no surrounding mines).
        """
        return not self._tile_grid[row, col].is_mine() and not self._is_tile_a_indicator(row, col)

    def _is_tile_a_indicator(self, row: int, col: int) -> bool:
        """
        Indicator tile represent the tile that has a number on it representing number of mines around it.
        0 means it is not a indicator.
        """
        return self._mine_count_grid[row, col] > 0

    def _set_up_grid(self):
        self._init_grids()
        self._place_random_mines()
        self._generate_indicators()

    def _init_grids(self):
        for row in range(self._grid_height):
            for col in range(self._grid_width):
                self._tile_grid[(row, col)] = Tile()
                self._mine_count_grid[(row, col)] = 0

    def _place_random_mines(self):
        for _ in range(self._mine_count):
            while True:
                row, col = self._generate_rnd_position()
                tile = self._tile_grid[row, col]
                if not tile.is_mine():
                    tile.place_mine()
                    break

    def _generate_indicators(self):
        for row in range(self._grid_height):
            for col in range(self._grid_width):
                if not self._tile_grid[row, col].is_mine():
                    self._mine_count_grid[row, col] = self._find_surrounding_mine_count(row, col)

    def _generate_rnd_position(self) -> Tuple[int, int]:
        row = random.randint(0, self._grid_height - 1)
        col = random.randint(0, self._grid_width - 1)
        return row, col

    def _find_surrounding_mine_count(self, row: int, col: int) -> int:
        count = 0

        for relative_location in Grid.ROTATIONS:
            try:
                location = (row + relative_location[0], col + relative_location[1])
                if self._tile_grid[location].is_mine():
                    count += 1
            except KeyError:
                # No need to check if index is in range for each call
                # Just ignore the exception
                pass

        return count

    def restart_grid(self):
        """
        Restarts grids to the original state.
        Result is the same grids states as when the object was initialized.
        """

        self._tile_grid = {}
        self._mine_count_grid = {}
        self._set_up_grid()

    def open_tile(self, row: int, col: int) -> List[Tuple[int, int], ]:
        """
        Returns all tiles that need to be revealed if the users clicks tile on passed row, col location.
        This will also update internal state of grid (marks tiles as revealed based on returned tiles).
        Return is useful for non-console applications where GUI needs to be updated.

        Algorithm is simple - for each tile, starting with passed tile location, check 8 directions:
        top-left, left, bottom-left, bottom, bottom-right, right, top-right, top
        1. If the checked tile is a mine then ignore
        2. If it's an empty tile then add it in list 'to_check' (don't add if already exists)
        3  If it's a empty tile with indicator on it, add it in 'to_not_check' list (don't add if already exists)
        After all 8 directions are checked we do the same thing for all the elements in 'to_check' list.


        We don't check directions for 'to_not_check' because that is our wall aka end of check, we don't
        go further than wall (wall = empty tile with indicator).
        Reason why mine tile is not our actual wall instead is if it were we would reveal all tiles except bombs!
        This would make it too easy to play! Only case where we would not reveal all tiles is if bombs form a closed
        area, which would still be unbalanced.

        So our wall is actually indicators aka the tiles NEXT to bombs.
        Note that revealed tiles are also our wall, we do not check them or go beyond them.

        We ignore the above algorithm in 2 cases:
        If the passed tile location is a mine.
        If the passes tile location is already revealed.
        In these 2 cases we only return passed tile location like [(row, col)]
        """

        to_check = [(row, col)]
        to_not_check = []

        curr_tile = self._tile_grid[row, col]
        if curr_tile.is_mine() or curr_tile.is_revealed():
            return to_check

        curr_tile.mark_as_revealed()

        def rotate_algorithm(curr_r, curr_c):
            for relative_location in Grid.ROTATIONS:
                try:
                    location = (curr_r + relative_location[0], curr_c + relative_location[1])
                    if self.is_tile_empty(*location) and not self._tile_grid[location].is_revealed() and not self._tile_grid[location].is_flagged():
                        if location not in to_check:
                            self._tile_grid[location].mark_as_revealed()
                            to_check.append(location)
                    elif self._is_tile_a_indicator(*location) and not self._tile_grid[location].is_revealed() and not self._tile_grid[location].is_flagged():
                        if location not in to_not_check:
                            self._tile_grid[location].mark_as_revealed()
                            to_not_check.append(location)
                except KeyError:
                    # No need to check if index is in range for each call
                    # Just ignore the exception
                    pass

        for location in to_check:
            rotate_algorithm(location[0], location[1])

        opened_tiles = to_check + to_not_check
        print(opened_tiles)
        return opened_tiles

    def check_win(self) -> bool:
        """
        Check if game is won.

        There are 2 conditions for win:
          ALL mines have to be correctly flagged.
          ALL other tiles (other than the flagged ones) have to be revealed - this prevents lucky flag at the end game.
        """
        return all((tile.is_flagged() and tile.is_mine()) or (tile.is_revealed() and not tile.is_mine()) for tile in self._tile_grid.values())

    def cheat(self):
        """
        Prints out entire grid along with all data and mines revealed.
        """
        print("Cheat:")
        visualization = []
        for row in range(self._grid_height):
            for col in range(self._grid_width):
                if self._tile_grid[row, col].is_mine():
                    visualization.append("X")
                else:
                    visualization.append(str(self._mine_count_grid[row, col]))
            visualization.append("\n")
        print("".join(visualization))

    @staticmethod
    def check_valid_grid_arguments(grid_height: int, grid_width: int, mine_count: int):
        """
        Check that will raise a exception if grid is not set up properly.

        Parameters:
            Both width and height cannot be smaller than 5.
            There has to be at least 1 mine and there cannot be more mines than possible tiles (grid size).
        :raise Exception: if any of the parameters are broken
        """
        grid_size = grid_height * grid_width

        if grid_height < 5 or grid_width < 5:
            raise Exception("Invalid grid size - too small")
        elif mine_count < 1:
            raise Exception("Invalid grid mine count - at least 1 mine required")
        elif mine_count > grid_size:
            raise Exception("Invalid grid mine count - can't have more tiles than grid size!")

    @staticmethod
    def generate_seed() -> int:
        return int.from_bytes(urandom(16), "big")
