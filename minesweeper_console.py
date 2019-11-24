import argparse
from backend.grid import Grid


class MinesweeperConsole:
    def __init__(self, grid_height: int, grid_width: int, mine_count: int, *, seed: int = None, cheat: bool = False):
        self.game = Grid(grid_height, grid_width, mine_count, seed=seed)
        self.play_game(cheat)

    def play_game(self, cheat: bool):
        if cheat:
            self.game.cheat()

        while True:
            print("-" * 100)
            print(" " + str(self.game))
            row, col, flag = MinesweeperConsole.get_user_input()
            if flag:
                self.game.get_tile(row, col).place_flag()
            else:
                self.game.open_tile(row, col)
            if self.game.check_win():
                print("You've won!")
                break

    @staticmethod
    def get_user_input():
        while True:
            user_input = input("Enter 'row col flag' or to just open tile 'row col':").split()
            if len(user_input) == 2:
                return int(user_input[0]), int(user_input[1]), False
            elif len(user_input) == 3:
                return int(user_input[0]), int(user_input[1]), True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument("grid_height", type=int, default=5, nargs="?", help="Height (rows) of the grid. Default 5.")
    parser.add_argument("grid_width", type=int, default=5, nargs="?", help="Width (columns) of the grid. Default 5.")
    parser.add_argument("mine_count", type=int, default=10, nargs="?", help="Mine count to be placed. Default 10.")
    parser.add_argument("-seed", type=int, default=None, help="Seed for pseudo-random generation. Default None.")
    parser.add_argument("-cheat", type=int, default=False, help="Reveal grid before game. Default 0 (False).")

    args = parser.parse_args()
    game = MinesweeperConsole(args.grid_height, args.grid_width, args.mine_count, seed=args.seed, cheat=args.cheat)
