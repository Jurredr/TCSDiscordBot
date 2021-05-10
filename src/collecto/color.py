from enum import Enum

reset = "\033[0m"


class Color(Enum):
    Blue = {"code": 1, "colorCode": "\033[38;2;0;0;255m", "backgroundColor": "\033[48;2;0;0;255m"}
    Yellow = {"code": 2, "colorCode": "\033[38;2;255;255;0m", "backgroundColor": "\033[48;2;255;255;0m"}
    Red = {"code": 3, "colorCode": "\033[38;2;255;0;0m", "backgroundColor": "\033[48;2;255;0;0m"}
    Orange = {"code": 4, "colorCode": "\033[38;2;255;140;0m", "backgroundColor": "\033[48;2;255;144;0m"}
    Purple = {"code": 5, "colorCode": "\033[38;2;153;0;153m", "backgroundColor": "\033[48;2;153;0;153m"}
    Green = {"code": 6, "colorCode": "\033[38;2;20;148;20m", "backgroundColor": "\033[48;2;20;175;20m"}
    Empty = {"code": 0, "colorCode": "", "backgroundColor": ""}

    def __hash__(self):
        return self.value["code"]

    def __repr__(self):
        return self.name
