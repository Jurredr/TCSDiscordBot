# from collecto import Board
from src.collecto.board import Board
from src.collecto.color import Color
import unittest


class TestBoard(unittest.TestCase):
    def setUp(self):
        self.board = Board()
        self.board.generate_board()
        # print(self.board)


class TestEmptySpace(TestBoard):
    def test_repeated_empty(self):
        for i in range(100):
            print(i)
            self.board.generate_board()
            self.test_center_empty()
            self.test_others_not_empty()
            self.test_color_frequencies()
            self.test_colors_not_adjacent()

    def test_center_empty(self):
        # assert self.board.balls[3][3] == Color.Empty, "Should be empty"
        # self.board.generate_board()
        self.assertEqual(self.board.balls[3][3].color, Color.Empty, self.board)

    def test_others_not_empty(self):
        for i in range(self.board.SIZE):
            for j in range(self.board.SIZE):
                if i != 3 and j != 3:
                    self.assertNotEqual(self.board.balls[i][j], Color.Empty, self.board)

    def test_color_frequencies(self):
        frequencies = {}

        for ballRow in self.board.balls:
            for ball in ballRow:
                frequencies[ball.color] = frequencies.get(ball.color, 0) + 1

        for color in Color:
            if color == Color.Empty:
                self.assertEqual(frequencies[color], 1, self.board)
            else:
                self.assertEqual(frequencies[color], 8, str(self.board) + "\n" + str(self.board.balls))

    def test_colors_not_adjacent(self):
        for i in range(self.board.SIZE):
            for j in range(self.board.SIZE):
                self.assertFalse(self.board.compare_balls(i, j, i - 1, j), "i={} j={}\n".format(i, j) + str(self.board))
                self.assertFalse(self.board.compare_balls(i, j, i, j - 1), "i={} j={}\n".format(i, j) + str(self.board))
                self.assertFalse(self.board.compare_balls(i, j, i + 1, j), "i={} j={}\n".format(i, j) + str(self.board))
                self.assertFalse(self.board.compare_balls(i, j, i, j + 1), "i={} j={}\n".format(i, j) + str(self.board))

    def test_copy(self):
        copy_board = self.board.__copy__()
        self.assertFalse(copy_board is self.board)
        print()
        print(copy_board)

        for i in range(self.board.SIZE):
            for j in range(self.board.SIZE):
                self.assertEqual(self.board.balls[i][j].color, copy_board.balls[i][j].color)
                self.assertFalse(self.board.balls[i][j] is copy_board.balls[i][j])


if __name__ == '__main__':
    unittest.main()
