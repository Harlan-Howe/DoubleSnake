import numpy as np
from copy import deepcopy
import random
import cv2
from typing import List, Tuple

# define new types, "Coord," "Move," and "Possible_Moves_List," for type hinting
Coord = Tuple[int, int]  # ideally two integers
Move = Tuple[Coord, int]
Possible_Moves_List = List[Move]

PLAYER_0_CODE = -1
PLAYER_1_CODE = +1
PLAYER_CHIPS = ["o", "*"]
PLAYER_CHARACTERS = ["O", "X"]

RELATIVE_MOVES = [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]

ARROW_COORDINATES = (((-0.4, 0), (+0.4, 0), (0, 0.25), (0, -0.25)),
                     ((-0.29, -0.29), (0.29, 0.29), (0.29, 0), (0, 0.29)),
                     ((0, -0.4), (0, +0.4), (0.25, 0), (-0.25, 0)),
                     ((0.29, -0.29), (-0.29, 0.29), (-0.29, 0), (0, 0.29)),
                     ((0.4, 0), (-0.4, 0), (0, 0.25), (0, -0.25)),
                     ((0.29, 0.29), (-0.29, -0.29), (-0.29, 0), (0, -0.29)),
                     ((0, 0.4), (0, -0.4), (-0.25, 0), (0.25, 0)),
                     ((-0.29, 0.29), (0.29, -0.29), (0.29, 0), (0, -0.29)))

GAME_MODE_6 = 0
GAME_MODE_10 = 1
GAME_MODE_14 = 2


class Board:
    def __init__(self, board_size: int = 8, board_to_copy: "Board" = None, game_mode: int = GAME_MODE_10):
        """
        creates either an empty board that is boardSize x boardSize OR a duplicate of an existing board.
        :param board_size: an odd integer
        :param board_to_copy: another Board object.
        Note: the board_size XOR the board_to_copy should be provided, but if both are, the board size will be ignored.
        """
        if board_to_copy is None:
            self.board_array = np.zeros((board_size, board_size), dtype=int)

            # set the range of non-zero cells... to expedite scoring.
            self.min_r = 0
            self.max_r = board_size
            self.min_c = 0
            self.max_c = board_size

            self.cell_size = 30
            self.screen_size = (self.cell_size * board_size, self.cell_size * board_size, 3)
            self.player_locations: List[List[Move]] = [[((int(board_size / 2) - 1, int(board_size / 2) - 1), 0),
                                                        ((int(board_size / 2) - 1, int(board_size / 2) - 2), 4)],
                                                       [((int(board_size / 2), int(board_size / 2)), 4),
                                                        ((int(board_size / 2), int(board_size / 2) + 1), 0)]]
            self.board_array[self.player_locations[0][0][0][0]][self.player_locations[0][0][0][1]] = PLAYER_0_CODE
            self.board_array[self.player_locations[0][1][0][0]][self.player_locations[0][1][0][1]] = PLAYER_0_CODE
            self.board_array[self.player_locations[1][0][0][0]][self.player_locations[1][0][0][1]] = PLAYER_1_CODE
            self.board_array[self.player_locations[1][1][0][0]][self.player_locations[1][1][0][1]] = PLAYER_1_CODE

            self.game_mode = game_mode
        else:
            self.board_array = deepcopy(board_to_copy.board_array)
            # copy the range of non-zero cells... to expedite scoring.
            self.max_r = board_to_copy.max_r
            self.min_r = board_to_copy.min_r
            self.max_c = board_to_copy.max_c
            self.min_c = board_to_copy.min_c

            # copy other variables of importance
            self.screen_size = board_to_copy.screen_size
            self.cell_size = board_to_copy.cell_size
            self.player_locations = deepcopy(board_to_copy.player_locations)
            self.game_mode = board_to_copy.game_mode

        # this is a dictionary of lists of the values stored in all possible runs, stored by length.
        # DEPRECATED
        # self.window_frames = {}

    def get_possible_moves(self, randomize: bool = False) -> List[Possible_Moves_List]:
        """
        determines a list of coordinates where the player is allowed to make a move.
        :param: whether to randomize the order of the resulting list.
        :return: a list of [r,c] values where a player may legally move next.
        """

        responses = []
        # loop over both players
        for player in range(2):
            player_response = []
            # loop over both ends of the players' snakes
            for end in range(2):
                end_response = []
                # where is this end now?
                start_loc = self.player_locations[player][end][0]
                direction = self.player_locations[player][end][1]

                if self.game_mode == GAME_MODE_6:
                    relative_headings = [direction, (direction + 2) % 8, (direction + 6) % 8]
                elif self.game_mode == GAME_MODE_10:
                    relative_headings = [direction, (direction+1) % 8, (direction+2) % 8,
                                         (direction+6) % 8, (direction+7) % 8]
                else:
                    relative_headings = [direction, (direction+1) % 8, (direction+2) % 8,
                                         (direction+3) % 8, (direction+5) % 8, (direction+6) % 8, (direction+7) % 8]
                for rel in relative_headings:
                    new_pos: Coord = (start_loc[0]+RELATIVE_MOVES[rel][0], start_loc[1]+RELATIVE_MOVES[rel][1])
                    if new_pos[0] < self.min_c or new_pos[1] < self.min_r \
                            or new_pos[0] > self.max_c-1 or new_pos[1] > self.max_r-1:
                        continue
                    if self.board_array[new_pos[0], new_pos[1]] == 0:
                        potential_move: Move = (new_pos, rel)
                        end_response.append(potential_move)

                player_response.extend(end_response)
            # randomize order of presented options, if desired....
            if randomize:
                temp: Possible_Moves_List = []
                while len(player_response) > 0:
                    loc = random.randint(0, len(player_response) - 1)
                    temp.append(player_response[loc])
                    del (player_response[loc])
                player_response = temp

            # add this list of responses to the list of response lists (one list per player)
            responses.append(player_response)

        return responses

    def make_move_for_player(self, move: Move, which_player: int):
        """
        Changes the state of this board so that the square at the selected move is set to which_player's code number,
        and the player position of which_player's end is updated to the move.
        Note: Assumes that this move will be a legal one.
        :param move: the (r,c) location where we should put a chip, and the direction (0-7) this move entails
        :param which_player: should we place PLAYER_0_CODE or PLAYER_1_CODE here? (0 or 1 values accepted.)
        :return: None
         NOTE: THIS METHOD ALTERS self.board
        """
        if which_player == 0:
            player_code = PLAYER_0_CODE
        else:
            player_code = PLAYER_1_CODE

        move_coord: Coord = move[0]
        move_direction: int = move[1]
        self.board_array[move_coord[0]][move_coord[1]] = player_code
        # where must we have come from?
        old_loc: Coord = (move_coord[0] + RELATIVE_MOVES[(move_direction + 4) % 8][0],
                          move_coord[1] + RELATIVE_MOVES[(move_direction + 4) % 8][1])

        made_move = False
        for which_end in range(2):  # consider both ends of this snake....
            if self.player_locations[which_player][which_end][0] == old_loc:
                self.player_locations[which_player][which_end] = move
                made_move = True
                break

        if not made_move:
            print(f"Error! Could not make illegal move: {move} for player {which_player}")
            print(f"{self.player_locations[which_player][0][0]=}")
            print(f"{self.player_locations[which_player][1][0]=}")
            print(f"{old_loc=}")

    def __str__(self):
        """
        gets a string representation of this board.
        :return:
        """
        result = ""
        r = 0
        for line in self.board_array:
            row = ""
            c = 0
            for item in line:
                found_player = False
                for player in range(2):
                    for end in range(2):
                        if self.player_locations[player][end][0] == (r, c):
                            row += PLAYER_CHARACTERS[player]
                            found_player = True
                            break
                if not found_player:
                    if item == PLAYER_0_CODE:
                        row += PLAYER_CHIPS[0]
                    elif item == PLAYER_1_CODE:
                        row += PLAYER_CHIPS[1]
                    else:
                        row += "·"
                c += 1
            result += row + "\n"
            r += 1
        return result

    def show_board(self, cell_size: int = 30):
        """
        displays a graphical version of the board.
        :param cell_size: how many pixels wide the cells are
        :return: None
        """
        self.cell_size = cell_size
        board_image = np.ones([self.board_array.shape[0] * cell_size, self.board_array.shape[1] * cell_size, 3],
                              dtype=float)
        self.screen_size = board_image.shape
        board_image[:, :, 0] *= 0.8
        # draw grid
        for i in range(self.board_array.shape[0]):
            cv2.line(board_image, (0, int(i*cell_size)), (board_image.shape[1]-1, int(i*cell_size)), (0, 0, 0), 1)
        for i in range(self.board_array.shape[1]):
            cv2.line(board_image, (int(i*cell_size), 0), (int(i*cell_size), board_image.shape[0]-1), (0, 0, 0), 1)

        # draw any/all circles
        center_cell = cell_size/2
        for r in range(self.board_array.shape[0]):
            for c in range(self.board_array.shape[1]):
                if self.board_array[r][c] == PLAYER_0_CODE:
                    cv2.circle(board_image, (int(center_cell + c * cell_size), int(center_cell + r * cell_size)),
                               int(4 * cell_size / 10), [0, 1, 0], -1)
                if self.board_array[r][c] == PLAYER_1_CODE:
                    cv2.circle(board_image, (int(center_cell + c * cell_size), int(center_cell + r * cell_size)),
                               int(4 * cell_size / 10), [0, 0.4, 0.8], -1)

        # draw any/all arrows
        arrow_colors = ((0, 0, 0), (1.0, 1.0, 1.0))
        for player in range(2):
            for end in range(2):
                loc, direction = self.player_locations[player][end]
                p = []
                for i in range(4):
                    p.append((int((0.5 + loc[1] + ARROW_COORDINATES[direction][i][0]) * cell_size),
                              int((0.5 + loc[0] + ARROW_COORDINATES[direction][i][1]) * cell_size)))
                cv2.line(board_image, p[0], p[1], arrow_colors[player], 1)
                cv2.line(board_image, p[2], p[1], arrow_colors[player], 1)
                cv2.line(board_image, p[3], p[1], arrow_colors[player], 1)

        cv2.imshow("Board", board_image)
        cv2.moveWindow("Board", 0, 0)
        # Wait one millisecond - this allows the computer time to display the change.
        # Without it, the window won't update.
        cv2.waitKey(1)

    def get_move_loc_for_click_loc(self, loc: Tuple[int, int]) -> Coord:
        """
        convert the (x,y) click on the screen to a corresponding (r,c) of which space was chosen.
        :param loc:
        :return:
        """
        r = int(loc[1]/self.cell_size)
        c = int(loc[0]/self.cell_size)
        return r, c

    def is_legal_for_player(self, loc: Coord, which_player: int):
        for m in self.get_possible_moves()[which_player]:
            if loc == m[0]:
                return True
        return False
