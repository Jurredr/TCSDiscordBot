class MoveNotPossibleError(Exception):
    pass


class InvalidMoveNumberError(Exception):
    def __init__(self, number):
        super("Move number {} is invalid".format(number))


def create_message2(position, direction):
    return "Move " + str(direction) + " at position " + str(position + 1) + " is not possible"


def create_message4(position1, direction1, position2, direction2):
    return "Double move with first move " + str(direction1) + " at position " + str(position1) + \
           " and second move " + str(direction2) + " at position " + \
           str(position2) + " is not possible"


def create_message1(position):
    return "Invalid move, position " + str(position) + " invalid, position should be between 0 and 6"
