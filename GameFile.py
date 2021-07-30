import numpy as np

from PlayerFile import Player
from HumanPlayerFile import HumanPlayer
from OneStepPlayerFile import OneStepPlayer
# from MinimaxPlayerFile import MinimaxPlayer
# from ABMinimaxPlayerFile import ABMinimaxPlayer
from DSBoard import Board, Coord, Move, Possible_Moves_List, GAME_MODE_6, GAME_MODE_10, GAME_MODE_14
import datetime
from typing import Tuple, List

import cv2

PLAYER_CHARACTERS = ["O", "X"]

DISPLAY_BOARD_AS_TEXT = True
DISPLAY_BOARD_AS_GRAPHICS = True

WAITING_FOR_FIRST_CLICK = 1000  # a dummy value for whose turn it is so that the timer doesn't start until the mouse is
#                                    clicked.


class Game:
    def __init__(self, board_size: int = 10, time_per_move: float = 30.0, game_mode: int = GAME_MODE_6):

        # board_size should be even.
        if board_size % 2 != 0:
            print(f"Hey! The board size ({board_size}) should be even! I'll do what I can with this odd number.")
        self.board = Board(board_size=board_size, game_mode=game_mode)
        self.time_per_move = time_per_move
        self.current_player = 0
        self.captured_pieces = [0, 0]
        self.players = (None, None)
        self.game_over = False
        self.stopwatch_start = datetime.datetime.now()

    def play_game(self, player1: Player = None, player2: Player = None):
        """
        The main game loop, given a set of players.
        :param player1: A Player object. If one is not provided, then it will use a generic Player().
        :param player2: Another Player object. If one is not provided, then it will use a generic Player().
        :return: None
        """
        # Create generic players, if we didn't receive any.
        if player1 is None:
            player1 = Player()
        if player2 is None:
            player2 = Player()

        # put our two players into a short list, for storage.
        self.players = (player1, player2)

        # Display board with "wait for click" message if we are in graphics mode
        #    and there is at least one human playing.
        if DISPLAY_BOARD_AS_GRAPHICS:
            self.display_board()
            if self.players[0].is_human() or self.players[1].is_human():
                cv2.setMouseCallback("Board", self.handle_click)  # be ready to receive and handle clicks.
                self.current_player = WAITING_FOR_FIRST_CLICK    # neither player 0 nor 1 yet - we're waiting to start
                #                                                   the game.
                print("Click mouse in board to start.")
                while self.current_player == WAITING_FOR_FIRST_CLICK:
                    cv2.waitKey(1)
                self.current_player = 0
            print("Starting game.")

        self.game_over = False

        # allow both players to preload data.
        if self.load_players():
            return

        previous_move = None
        # Get list of possible initial moves... this will be refreshed at the end of each loop.
        possible_moves: List[Possible_Moves_List] = self.board.get_possible_moves()

        # Main loop.........................................................................
        while not self.game_over:
            print(f"Player {PLAYER_CHARACTERS[self.current_player]} to move...")

            self.restart_stopwatch()

            print("-----------------")
            move: Move = self.players[self.current_player].select_move(board=Board(board_to_copy=self.board),
                                                                       which_player_am_I=self.current_player,
                                                                       get_expired_time_method=self.expired_time_in_s,
                                                                       opponents_move=previous_move)
            # "click the stopwatch for (time spent, time remaining).
            expired = self.expired_time_in_s()
            if expired[1] < 0:
                print(f"Player {PLAYER_CHARACTERS[self.current_player]} took too long to move: {expired[0]}.")
                self.game_over = True
                break
            print(f"Player {PLAYER_CHARACTERS[self.current_player]} chose to move to (x,y) = \
                {move} in {expired[0]} seconds.")

            if move not in possible_moves[self.current_player]:
                print("This is an illegal move.")
                self.game_over = True
                break

            # During play, the players may have made copies of the board and moved on those copies. But this line makes
            #   the actual move.
            self.board.make_move_for_player(move=move, which_player=self.current_player)

            self.display_board()

            # check to see whether this player has won.
            other_player = 1 - self.current_player

            possible_moves = self.board.get_possible_moves()
            if len(possible_moves[other_player]) == 0:
                self.game_over = True
                print("Game Over!")
                break
            # Otherwise, swap players.
            self.current_player = other_player

            # record the move that was just made, so we can tell the next player about it.
            previous_move = move


    def handle_click(self, event: int, x: int, y: int, flags: int, param):
        """
        this method gets called whenever the user moves or clicks or does
        anything mouse-related while the mouse is in the "Board" window.
        In this particular case, it will only do stuff if the mouse is being
        released.
        :param event: what kind of mouse event was this?
        :param x:
        :param y:
        :param flags: I suspect this will be info about modifier keys (e.g. shift)
        :param param: additional info from cv2... probably unused.
        :return: None
        """
        if self.game_over:
            return
        if event == cv2.EVENT_LBUTTONUP:  # only worry about when the mouse is released inside this window.
            print("handling a click.")
            if self.current_player == WAITING_FOR_FIRST_CLICK:
                print("first click.")
                self.current_player = 0
                return

            if self.players[self.current_player].is_human():
                print(f"Click for player {self.current_player} at ({x}, {y}).")
                self.players[self.current_player].handle_click_at_xy_point((x, y))
                return

    def load_players(self):
        """
        Allows both players to pre-load some data (if desired), as long as it takes less than
        the amount of time per move.
        :return: whether either player exceeded the time limit.
        """
        for i in range(2):
            self.restart_stopwatch()
            print(f"Player {i} loading data.")
            self.players[i].load_data(board=self.board,
                                      which_player_am_I=i,
                                      get_expired_time_method=self.expired_time_in_s)
            if self.expired_time_in_s()[1] < 0:
                print(f"Player {i} exceeded load time.")
                self.game_over = True
                return True
            print(f"Player {i} loaded in {self.expired_time_in_s()} seconds.")
        return False

    def restart_stopwatch(self):
        """
        resets the stopwatch used by the expired_time_in_s(self) method
        :return: None
        """
        self.stopwatch_start = datetime.datetime.now()

    def expired_time_in_s(self) -> Tuple[float, float]:
        """
        gets the number of seconds since the last time we called restart_stopwatch, and how much time remains before we
        reach self.time_per_move
        :return: (seconds_expired, time_remaining) - floats, in seconds
        """
        elapsed = datetime.datetime.now() - self.stopwatch_start
        return elapsed.total_seconds(), self.time_per_move-elapsed.total_seconds()

    def display_board(self):
        """
        routes the display function to text and/or graphics, as appropriate
        :return: None
        """
        if DISPLAY_BOARD_AS_TEXT:
            print(self.board)

        if DISPLAY_BOARD_AS_GRAPHICS:
            self.board.show_board()


# These are the commands that start the game.....
if __name__ == '__main__':
    # create a Game and start it running
    the_game = Game(board_size=8, time_per_move=15, game_mode=GAME_MODE_6)
    the_game.play_game(HumanPlayer(), Player())

    # Display a "game over" window. Comment this out if you wish to loop over many games.
    game_over_window = np.ones((50, 200, 3), dtype=float)
    cv2.putText(game_over_window, "Game Over", (10, 45),
                cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0))
    cv2.imshow("Game Over", game_over_window)
    cv2.moveWindow("Game Over", 0, the_game.board.screen_size[0] + 0)

    # the game is over... display the board, but encourage the user to click once more to quit.
    if DISPLAY_BOARD_AS_GRAPHICS:
        print("Click in the window and press any key to quit.")
        # once the game is over, we want the screen to stay up, until the user presses a key,
        # so we wait indefinitely until the user does, and then dispose of the window.
        cv2.waitKey(0)
        cv2.destroyAllWindows()
