import copy
import sys

from src.collecto.exceptions import MoveNotPossibleError, InvalidMoveNumberError, create_message1, create_message2, create_message4
from src.collecto.color import Color, reset
# from src.collecto import Color
from src.collecto.ball import Ball
from random import randint

UP = "UP"
DOWN = "DOWN"
LEFT = "LEFT"
RIGHT = "RIGHT"
SIZE = 7


def get_position_from_number(number):
    if number < 0 or number >= 4 * SIZE:
        raise InvalidMoveNumberError(number)
    else:
        return number % SIZE


def get_direction_from_number(number):
    if 0 <= number < SIZE:
        return LEFT
    elif SIZE <= number < 2 * SIZE:
        return RIGHT
    elif 2 * SIZE <= number < 3 * SIZE:
        return UP
    elif 3 * SIZE <= number < 4 * SIZE:
        return DOWN
    else:
        raise InvalidMoveNumberError(number)


class Board:
    def __init__(self):
        self.SIZE = 7
        self.balls = []

        # for i in range(self.SIZE):
        #     self.balls.append([])
        #     for j in range(self.SIZE):
        #         self.balls[i].append(None)

        self.UP = "UP"
        self.DOWN = "DOWN"
        self.LEFT = "LEFT"
        self.RIGHT = "RIGHT"
        sys.setrecursionlimit(10 ** 6)

    def __copy__(self):
        new_board = Board()
        new_board.balls = copy.deepcopy(self.balls)
        return new_board

    def generate_board(self):
        self.balls.clear()
        possible_colors = set({color for color in Color})
        # print(possible_colors)
        possible_colors.remove(Color.Empty)
        # print(possible_colors)

        color_counter = {}

        for color in possible_colors:
            color_counter[color] = 8

        for i in range(self.SIZE):
            self.balls.append([])
            for j in range(self.SIZE):
                # print(str(i) + " " + str(j))
                if i == 3 and j == 3:
                    self.balls[i].append(Ball(Color.Empty))
                else:
                    possible_colors_here = possible_colors.copy()
                    # print(possible_colors_here)
                    try:
                        # remove color from the left of position
                        # print(i - 1)
                        # print(j)
                        possible_colors_here.remove(self.balls[i - 1][j].color)
                    except (IndexError, KeyError, AttributeError):
                        pass

                    try:
                        # remove color from above position
                        possible_colors_here.remove(self.balls[i][j - 1].color)
                    except (IndexError, KeyError, AttributeError):
                        pass

                    try:
                        random = randint(0, len(possible_colors_here) - 1)
                        # print(random)
                        new_color = list(possible_colors_here)[random]
                        # print(new_color)
                        # print(str(i) + " " + str(j))
                        self.balls[i].append(Ball(new_color))

                        counter = color_counter[new_color]
                        counter -= 1
                        color_counter[new_color] = counter

                        if counter == 0:
                            possible_colors.remove(new_color)
                    except ValueError:
                        self.generate_board()
                        return

        if not self.is_playable():
            self.generate_board()

    def is_playable(self):
        for i in range(3):
            if self.compare_balls(i, 3, i + 1, 3) or self.compare_balls(i, 3, i + 1, 4) or \
                    self.compare_balls(3, i, 2, i + 1) or self.compare_balls(3, i, 4, i + 1) or \
                    self.compare_balls(i, 0, i + 1, 1) or self.compare_balls(i, 6, i + 1, 5) or \
                    self.compare_balls(0, i, 1, i + 1) or self.compare_balls(6, i, 5, i + 1):
                return True

        for i in range(self.SIZE - 1, 3, -1):
            if self.compare_balls(i, 3, i - 1, 2) or self.compare_balls(i, 3, i - 1, 4) or \
                    self.compare_balls(3, i, 2, i - 1) or self.compare_balls(3, i, 4, i - 1) or \
                    self.compare_balls(i, 0, i - 1, 1) or self.compare_balls(i, 6, i - 1, 5) or \
                    self.compare_balls(0, i, 1, i - 1) or self.compare_balls(6, i, 5, i - 1):
                return True

        return self.compare_balls(2, 3, 4, 3) or self.compare_balls(3, 2, 3, 4)

    def compare_balls(self, i1, j1, i2, j2):
        if i1 < 0 or j1 < 0 or i2 < 0 or j2 < 0:
            return False

        try:
            return self.balls[i1][j1] == self.balls[i2][j2]
        except IndexError:
            return False

    def check_adjacent_balls(self, i, j):
        return self.compare_balls(i, j, i + 1, j) or self.compare_balls(i, j, i, j + 1) or \
               self.compare_balls(i, j, i - 1, j) or self.compare_balls(i, j, i, j - 1)

    def make_move(self, position, direction):
        if position < 0 or position >= self.SIZE:
            raise MoveNotPossibleError(create_message1(position))
        elif not self.check_move(position, direction):
            raise MoveNotPossibleError(create_message2(position, direction))
        else:
            self.move_balls(position, direction)
            return self.remove_balls(position, direction)

    def make_double_move(self, position1, direction1, position2, direction2):
        if position1 < 0 or position1 >= SIZE:
            raise MoveNotPossibleError(position1)
        elif position2 < 0 or position2 >= SIZE:
            raise MoveNotPossibleError(position2)

        if self.single_move_possible():
            raise MoveNotPossibleError("Double move is not allowed," +
                                       "because a single move is possible")
        elif not self.check_double_move(position1, direction1, position2, direction2):
            raise MoveNotPossibleError(create_message4(position1, direction1, position2, direction2))
        else:
            self.move_balls(position1, direction1)
            self.move_balls(position2, direction2)
            return self.remove_balls(position2, direction2)

    def make_move_with_number(self, number):
        try:
            return self.make_move(get_position_from_number(number), get_direction_from_number(number))
        except MoveNotPossibleError:
            raise MoveNotPossibleError("Move with move number {} is not possible".format(number))

    def make_double_move_with_number(self, number1, number2):
        try:
            return self.make_double_move(get_position_from_number(number1), get_direction_from_number(number1),
                                         get_position_from_number(number2), get_direction_from_number(number2))
        except MoveNotPossibleError:
            raise MoveNotPossibleError("Double move with move number {} and {} is not possible".format(number1, number2))

    def check_move(self, position, direction):
        if position < 0 or position >= self.SIZE:
            return False

        test_board = self.__copy__()

        test_board.move_balls(position, direction)

        if direction == self.UP or direction == self.DOWN:
            for i in range(self.SIZE):
                if test_board.check_adjacent_balls(i, position):
                    return True
        elif direction == self.LEFT or direction == self.RIGHT:
            for i in range(self.SIZE):
                if test_board.check_adjacent_balls(position, i):
                    return True

        return False

    def check_double_move(self, position1, direction1, position2, direction2):
        if self.single_move_possible():
            return False
        else:
            test_board = self.__copy__()
            test_board.move_balls(position1, direction1)
            return test_board.check_move(position2, direction2)

    def check_move_with_number(self, number):
        return self.check_move(get_position_from_number(number), get_direction_from_number(number))

    def single_move_possible(self):
        for i in range(4 * SIZE):
            if self.check_move_with_number(i):
                return True

        return False

    def double_move_possible(self):
        if not self.single_move_possible():
            for i in range(4 * SIZE):
                test_board = self.__copy__()
                test_board.move_balls(get_position_from_number(i), get_direction_from_number(i))

                if test_board.single_move_possible():
                    return True
        else:
            return False

    def move_balls(self, position, direction):
        if direction == self.UP:
            self.move_up(position)
        elif direction == self.DOWN:
            self.move_down(position)
        elif direction == self.LEFT:
            self.move_left(position)
        elif direction == self.RIGHT:
            self.move_right(position)

    def move_up(self, column):
        nearest_empty = 0
        empty_found = False

        for i in range(self.SIZE):
            current_color = self.balls[i][column].color

            if current_color == Color.Empty and not empty_found:
                nearest_empty = i
                empty_found = True
            elif current_color != Color.Empty and empty_found:
                self.balls[nearest_empty][column] = self.balls[i][column]
                self.balls[i][column] = Ball(Color.Empty)
                nearest_empty += 1

    def move_down(self, column):
        nearest_empty = 0
        empty_found = False

        for i in range(self.SIZE - 1, -1, -1):
            current_color = self.balls[i][column].color

            if current_color == Color.Empty and not empty_found:
                nearest_empty = i
                empty_found = True
            elif current_color != Color.Empty and empty_found:
                self.balls[nearest_empty][column] = self.balls[i][column]
                self.balls[i][column] = Ball(Color.Empty)
                nearest_empty -= 1

    def move_left(self, row):
        nearest_empty = 0
        empty_found = False

        for i in range(self.SIZE):
            current_color = self.balls[row][i].color

            if current_color == Color.Empty and not empty_found:
                nearest_empty = i
                empty_found = True
            elif current_color != Color.Empty and empty_found:
                self.balls[row][nearest_empty] = self.balls[row][i]
                self.balls[row][i] = Ball(Color.Empty)
                nearest_empty += 1

    def move_right(self, row):
        nearest_empty = 0
        empty_found = False

        for i in range(self.SIZE - 1, -1, -1):
            current_color = self.balls[row][i].color

            if current_color == Color.Empty and not empty_found:
                nearest_empty = i
                empty_found = True
            elif current_color != Color.Empty and empty_found:
                self.balls[row][nearest_empty] = self.balls[row][i]
                self.balls[row][i] = Ball(Color.Empty)
                nearest_empty -= 1

    def remove_balls(self, position, direction):
        balls_to_remove = set()

        if direction == UP or direction == DOWN:
            for i in range(SIZE):
                if self.compare_balls(i, position, i, position - 1):  # Compares ball to the left
                    balls_to_remove.add(self.balls[i][position])
                    balls_to_remove.add(self.balls[i][position - 1])

                if self.compare_balls(i, position, i, position + 1):  # Compares ball to the right
                    balls_to_remove.add(self.balls[i][position])
                    balls_to_remove.add(self.balls[i][position + 1])

                if self.compare_balls(i, position, i + 1, position):  # Compares ball below
                    balls_to_remove.add(self.balls[i][position])
                    balls_to_remove.add(self.balls[i + 1][position])
        elif direction == LEFT or direction == RIGHT:
            for i in range(SIZE):
                if self.compare_balls(position, i, position - 1, i):  # Compares ball above
                    balls_to_remove.add(self.balls[position][i])
                    balls_to_remove.add(self.balls[position - 1][i])

                if self.compare_balls(position, i, position + 1, i):  # Compares ball below
                    balls_to_remove.add(self.balls[position][i])
                    balls_to_remove.add(self.balls[position + 1][i])

                if self.compare_balls(position, i, position, i + 1):  # Compares ball to the left
                    balls_to_remove.add(self.balls[position][i])
                    balls_to_remove.add(self.balls[position][i + 1])

        color_amounts = {}

        for ball in balls_to_remove:
            color_amounts[ball.color] = color_amounts.get(ball.color, 0) + 1
            ball.color = Color.Empty

        return color_amounts

    def __str__(self):
        row_divider = "  +---------+---------+---------+---------+---------+---------+---------+\n"
        column_numbers = "       1         2         3         4         5         6         7\n"
        result = column_numbers + row_divider

        for i in range(self.SIZE):
            for j in range(3):
                if j == 1:
                    result += str(i + 1) + " |"
                else:
                    result += "  |"

                for k in range(self.SIZE):
                    color = self.balls[i][k].color
                    result += " " + color.value["backgroundColor"] + " " * 7 + reset + " |"

                result += "\n"
            result += row_divider
        return result

# board = Board()
# board.generate_board()
# print(board.balls)
# print(board)
