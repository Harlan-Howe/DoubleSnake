import numpy as np
from copy import deepcopy
import random
from DSBoard import Board, Coord, Move, Possible_Moves_List
from typing import Tuple, List, Callable


class Player:
    """
    The base level Player. This one always picks the next move at random from the list of possibilities. Other players
    inherit from this class.
    """
    def __init__(self):
        pass

    def select_move(self, board: Board, which_player_am_I: int,
                    get_expired_time_method:Callable,
                    opponents_move: Move = None) -> Move:
        """
        given the state of the game, asks this player to pick a move, before time runs out.
        :param board: the current state of the board (a copy, as it turns out, so you can modify it.)
        :param which_player_am_I: Either 0 or 1
        :param get_expired_time_method: the method that can be called to determine how much time has expired and how
        much time remains. (These are returned as a list of two floats - units of seconds.)
        :param opponents_move - the move your opponent just made, if any. (None if this is a first move)
        :return: the coordinates of the move to be made, in (r, c) format.
        """
        # not used in this dopey class, but I think you'll find it handy in better ones.
        other_player = 1 - which_player_am_I

        potential_moves: List[Possible_Moves_List] = board.get_possible_moves(randomize=True)

        # not used in this class either, but likely to be useful in better ones.
        expired_time, remaining_time = get_expired_time_method()

        return potential_moves[which_player_am_I][0]  # return the first move on the list for this player.

    def load_data(self, board, which_player_am_I, get_expired_time_method):
        """
        loads any initial data values into this player - one time at start of game.
        :param board:
        :param which_player_am_I:
        :param get_expired_time_method:
        :return:
        """

        # Note: this method doesn't need to do anything at all if you don't want it to. This is a spot to upload
        # "starting moves" if you desire. Nevertheless, it still has to take a maximum of the time per move to do it!
        # Feel free to leave this method alone - it is just here as a option.
        print(f"Player {which_player_am_I} declines to preload data.")
        pass  # does nothing, for now.

    def is_human(self):
        """
        indicates whether this is a human player that will require the use of the mouse.
        :return: boolean
        """
        return False

    def score_for_board(self, board: Board, which_player_am_I: int = 0) -> int:
        return 1  # not really used in the base Player class.
