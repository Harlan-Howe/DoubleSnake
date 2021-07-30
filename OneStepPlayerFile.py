from PlayerFile import Player
from DSBoard import Board

class OneStepPlayer(Player):
    """
    A short-sighted player - it picks the move that will maximize the number of runs and/or captures this ply.
    """


    def __init__(self):
        pass

    def select_move(self, board, which_player_am_I, get_expired_time_method,opponents_move = None):
        #start with a random move...
        best_move = Player.select_move(self, board=board,
                                       which_player_am_I=which_player_am_I,
                                       get_expired_time_method=get_expired_time_method)
        best_score = 0
        #... and hopefully, we can do better.
        potential_moves = board.get_possible_moves(randomize=True)[which_player_am_I]
        for move in potential_moves:
            #bail out if we're about to run out of time....
            if get_expired_time_method()[1] < 0.01: # You can adjust this time (in seconds) to refine how close you wish to cut it....
                break

            score = self.get_score_for_move(board, which_player_am_I, move)

            if score>best_score:
                best_score = score
                best_move = move
        return best_move

    def get_score_for_move(self, board, which_player, move):
        """
        This is a blunt method for finding the score, and it does not take into account anything other than the move
        selected. In this simple example, it returns the number of moves this player would have available on the next
        turn... if this player got to move again immediately.
        :param board:
        :param which_player:
        :param move_loc:
        :return:
        """
        # What would this board look like if you made this move?
        board_copy = Board(board_to_copy = board)
        board_copy.make_move_for_player(move, which_player)

        return self.score_for_board(board_copy, which_player_am_I=which_player)

    def score_for_board(self, board: Board, which_player_am_I: int = 0) -> int:
        """
        bases the score on the number of possible moves this player has remaining.
        :param board:
        :param which_player_am_I:
        :return:
        """
        score = len(board.get_possible_moves()[which_player_am_I])

        return score
