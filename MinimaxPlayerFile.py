from typing import Callable, Optional, List, override, Tuple

from DSBoard import Board, Move, Possible_Moves_List
from PlayerFile import Player

class MinimaxPlayer(Player):
    """
    a "smart" (?) Player that looks several steps ahead
    """

    def __init__(self):
        super().__init__()

    @override
    def select_move(self, board: Board, which_player_am_I: int,
                    get_expired_time_method: Callable,
                    opponents_move: Optional[Move] = None) -> Move:
        """
        given the state of the game, asks this player to pick a move, before time runs out.
        :param board: the current state of the board (a copy, as it turns out, so you can modify it.)
        :param which_player_am_I: Either 0 or 1
        :param get_expired_time_method: the method that can be called to determine how much time has expired and how
        much time remains. (These are returned as a list of two floats - units of seconds.)
        :param opponents_move: - the move your opponent just made, if any. (None if this is a first move)
        :return: the coordinates of the move to be made, in (r, c) format.
        """

        # Here are three variable I think you might find handy...
        other_player = 1 - which_player_am_I
        potential_moves: List[Possible_Moves_List] = board.get_possible_moves(randomize=True)
        expired_time, remaining_time = get_expired_time_method() # tells the time NOW ... you may want to move this.

        return potential_moves[which_player_am_I][0]  # replace this with the move you actually want.

    def maximize_score(self,
                       board:Board,
                       which_player_am_I: int,
                       get_expired_time_method: Callable,
                       depth_to_go: int) -> Tuple[Move, int]:
        """
        selects the optimal move for this player to make, (i.e., the one yielding the highest score) looking
        "depth_to_go" plies ahead and assuming both players are picking moves as wisely as possible. In the case of a
        tie, picks between equivalent options randomly..
        :param board: the state of the board at the moment.
        :param which_player_am_I: 0 or 1... this is the player doing the asking.
        :param get_expired_time_method: a method to determine whether you need to bail out early and return.
        :param depth_to_go: number of steps to look ahead. If this is 0, return now.
        :return: the best move and the optimal score that goes with it, if both player are picking moves wisely..
        """
        pass


    @override
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
        # Feel free to leave this method alone - it is just here as an option.
        print(f"Player {which_player_am_I} declines to preload data.")
        pass  # does nothing, for now.

    @override
    def is_human(self):
        """
        indicates whether this is a human player that will require the use of the mouse.
        :return: boolean
        """
        return False

    @override
    def score_for_board(self,
                        board: Board, which_player_am_I: int = 0,
                        possible_moves_list: Optional[Possible_Moves_List] = None) -> int:
        """
        returns the number of available moves for this player, minus the number available to the opponent.
        NOTE: This is the prototype scoring method. You may wish to write something better.
        :param board: the board under consideration
        :param which_player_am_I: the number (0 or 1) of the player who is asking.
        :param possible_moves_list: the list of possible moves for this board. If None, this method will call the method
               to find it, but if you already have it, it will be faster to pass it than regenerate it.
        :return: the score.
        """
        if possible_moves_list is None:
            possible_moves_list = board.get_possible_moves()
        opponent = 1 - which_player_am_I
        return len(possible_moves_list[which_player_am_I]) - len(possible_moves_list[opponent])
