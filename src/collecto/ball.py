from src.collecto.color import Color


class Ball:
    def __init__(self, color):
        self.color = color

    def __eq__(self, other):
        if self is other:
            return True

        if isinstance(other, Ball):
            if self.color == Color.Empty or other.color == Color.Empty:
                return False

            else:
                return self.color == other.color

        return False

    def __hash__(self):
        return id(self)
