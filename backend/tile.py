class Tile:
    def __init__(self, mine: bool = False, revealed: bool = False, flagged: bool = False):
        """
        :param mine: bool has mine or not, defaults to False.
        :param revealed: bool revealed or not, defaults to False.
        :param flagged: bool flagged or not, defaults to False.
        """
        self._mine = mine
        self._revealed = revealed
        self._flagged = flagged

    def __str__(self):
        if self._revealed:
            if self._mine:
                return "X"
            else:
                return "-"
        elif self._flagged:
            return "?"
        else:
            return "+"

    def place_mine(self):
        self._mine = True

    def is_mine(self) -> bool:
        return self._mine

    def mark_as_revealed(self):
        self._revealed = True

    def is_revealed(self) -> bool:
        return self._revealed

    def place_flag(self):
        if self.is_revealed():
            print("Warning - Placing flag on a revealed tile.")
        self._flagged = True

    def remove_flag(self):
        self._flagged = False

    def is_flagged(self) -> bool:
        return self._flagged
