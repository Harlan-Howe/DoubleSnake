from PlayerFile import Player
from DSBoard import Board, Move, Possible_Moves_List, Coord
from typing import Tuple, List, Callable
import cv2
import numpy as np


class HumanPlayer (Player):
    """
    NOTE: This requires that the graphics version of Game is active, or the player will just pick randomly.
    """
    def __init__(self):
        super().__init__()
        self.waiting_for_mouse = True
        self.xy_click_loc = (0, 0)
        pass

    def select_move(self,
                    board: Board,
                    which_player_am_I: int,
                    get_expired_time_method: Callable,
                    opponents_move: Move = None) -> Move:
        """
        given the state of the game, asks this player to pick a move, before time runs out.
        :param board: the current state of the board (a copy, as it turns out, so you can modify it.)
        :param which_player_am_I: Either 0 or 1
        :param get_expired_time_method: the method that can be called to determine how much time has expired and how
        much time remains. (These are returned as a list of two floats.)
        :opponents_move
        :param opponents_move: the move that your opponent just made, in case that informs your decision
        :return: the coordinates of the move to be made, in (r, c) format.
        """
        best_move: Move = Player.select_move(self, board=board,
                                             which_player_am_I=which_player_am_I,
                                             get_expired_time_method=get_expired_time_method)
        possible_moves: List[Possible_Moves_List] = board.get_possible_moves(randomize=False)
        print(f"Possible moves: {possible_moves}")

        while True:
            self.waiting_for_mouse = True
            while self.waiting_for_mouse:
                if get_expired_time_method()[1] < 0.1:
                    print("Out of time. Picking random move.")
                    cv2.destroyWindow("Player Time")
                    return best_move
                cv2.waitKey(10)
                my_window = np.ones((50, 200, 3), dtype=float)
                if get_expired_time_method()[1] < 10 and int(2*get_expired_time_method()[1]) % 2 == 0:
                    my_window[:, :, 0] = 0
                    my_window[:, :, 1] = 0.5
                cv2.putText(my_window, "{0:3.1f}".format(get_expired_time_method()[1]), (10, 45),
                            cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0))
                cv2.imshow("Player Time", my_window)
                cv2.moveWindow("Player Time", 0, board.screen_size[0]+40)
            chosen_move_rc = board.get_move_loc_for_click_loc(self.xy_click_loc)
            print(f"{chosen_move_rc=}")
            for move in possible_moves[which_player_am_I]:
                print(move[0])
                if move[0] == chosen_move_rc:
                    cv2.destroyWindow("Player Time")
                    return move

            print("Not a legal move. Try again.")

    def handle_click_at_xy_point(self, pt: Tuple[int, int]):
        """
        update the self.xy_click_loc variable with the given point, and changes the self.waiting_for_mouse to illustrate
        that the wait is over.
        :param pt:
        :return: None
        """
        self.xy_click_loc = pt
        self.waiting_for_mouse = False
        print(f"Clicked at {pt}.")

    def is_human(self):
        return True
