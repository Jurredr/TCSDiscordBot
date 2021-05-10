from src.collecto.board import Board
import src.collecto.board
from src.collecto.exceptions import MoveNotPossibleError

board = Board()
board.generate_board()

move_codes = {"u": board.UP, "d": board.DOWN, "l": board.LEFT, "r": board.RIGHT}
points = {}

while board.single_move_possible() or board.double_move_possible():
    print(board)
    next_move = input("Enter next move: ").split(" ")

    if len(next_move) == 2 or len(next_move) == 3:
        try:
            direction = move_codes[next_move[0]]
        except KeyError:
            print("Direction invalid")
            continue

        try:
            position = int(next_move[1]) - 1
        except ValueError:
            print("Position is not numeric")
            continue

        try:
            move_points = board.make_move(position, direction)

            for color in move_points.keys():
                points[color] = points.get(color, 0) + move_points[color]

        except MoveNotPossibleError as e:
            print(e)
    elif len(next_move) >= 4:
        try:
            direction1 = move_codes[next_move[0]]
            direction2 = move_codes[next_move[2]]
        except KeyError:
            print("Direction invalid")
            continue

        try:
            position1 = int(next_move[1]) - 1
            position2 = int(next_move[3]) - 1
        except ValueError:
            print("Position is not numeric")
            continue

        try:
            move_points = board.make_double_move(position1, direction1, position2, direction2)

            for color in move_points.keys():
                points[color] = points.get(color, 0) + move_points[color]
        except MoveNotPossibleError as e:
            print(e)

print(board)
print(points)
