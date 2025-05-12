from enum import Enum
from typing import Tuple, List


class Params(Enum):
    FONT_FILE: str = "Prima Sans Bold.otf"
    FONT_DIRECTORY: str = "fonts"
    FONT_SIZE: int = 112
    FONT_COLOR: Tuple[int, int, int, int] = (252, 252, 252, 0)
    FONT_FEATURES: List[str] = ["-kern"]
    FONT_ALIGN: str = "center"
    HEIGHT_OFFSET: int = 64
    WIDTH: int = 960
    HEIGHT: int = 540
    FOREGROUND_WEIGHT: float = 0.5
    BACKGROUND_WEIGHT: float = 0.5
