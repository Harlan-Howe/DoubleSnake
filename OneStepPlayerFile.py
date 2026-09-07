from typing import Callable, Optional, List

from PlayerFile import Player
from DSBoard import Board, Move, Possible_Moves_List


class OneStepPlayer(Player):
    """
    A short-sighted player - it picks the move that will maximize the number of remaining available moves.
    """
    def __init__(self):
        super().__init__()

    def select_move(self,
                    board: Board,
                    which_player_am_I: int,
                    get_expired_time_method: Callable,
                    opponents_move: Optional[Move] = None) -> Move:

        # what moves are even options?
        potential_moves: List[Move] = board.get_possible_moves(randomize=True)[which_player_am_I]

        # start with a random move...
        best_move = potential_moves[0]
        best_score = 0

        # ... and hopefully, we can do better.

        for move in potential_moves:
            # Bail out if we're about to run out of time....
            if get_expired_time_method()[1] < 0.01:  # You can adjust this time (in seconds) to refine how close you
                #                                      wish to cut it....
                break

            score = self.get_score_for_move(board, which_player_am_I, move)

            if score > best_score:
                best_score = score
                best_move = move
        return best_move

    def get_score_for_move(self,
                           board: Board,
                           which_player: int,
                           move: Move):
        """
        This is a blunt method for finding the score, and it does not take into account anything other than the move
        selected. In this simple example, it returns the number of moves this player would have available on the next
        turn... if this player got to move again immediately.
        :param board:
        :param which_player:
        :param move:
        :return:
        """
        # What would this board look like if you made this move?
        board_copy = Board(board_to_copy=board)
        board_copy.make_move_for_player(move, which_player)

        # return the score for this new, proposed board arrangement.
        return self.score_for_board(board_copy, which_player_am_I=which_player)

    def score_for_board(self,
                        board: Board, which_player_am_I: int = 0,
                        possible_moves_list: Optional[Possible_Moves_List] = None) -> int:
        """
        bases the score on the number of possible moves this player has remaining.
        :param board:
        :param which_player_am_I:
        :param possible_moves_list: the list of possible moves for this board. If None, this method will call the method
               to find it, but if you already have it, it will be faster to pass it than regenerate it.
        :return:
        """
        if possible_moves_list is None:
            possible_moves_list = board.get_possible_moves()
        score = len(possible_moves_list[which_player_am_I])

        return score
