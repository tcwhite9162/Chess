from game.piece import Piece

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 640

BOARD_SIZE = 8
SQUARE_SIZE = 80  # Square size
RADIUS = 6        # Radius of legal move circles
CAPTURE_RING_WIDTH = 8    # Thickness of ring rendered on captures
CHECK_BORDER_WIDTH = 4    # Thickness of border around king's square when in check

BOARD_ORIGIN_X = 0  # Left margin
BOARD_ORIGIN_Y = 0  # Top margin

SIDEBAR_WIDTH = SCREEN_WIDTH - (BOARD_SIZE * SQUARE_SIZE) - BOARD_ORIGIN_X * 2  # Remaining space

def get_starting_position():
    return [
            [Piece("b", p, SQUARE_SIZE)   for p in ["r", "n", "b", "q", "k", "b", "n", "r"]],
            [Piece("b", "p", SQUARE_SIZE) for _ in range(8)],
            *[[None] * 8 for _ in range(4)],
            [Piece("w", "p", SQUARE_SIZE) for _ in range(8)],
            [Piece("w", p, SQUARE_SIZE)   for p in ["r", "n", "b", "q", "k", "b", "n", "r"]],
            ]

COLOR_PALETTES = {
    "classic": {
        "low": (    # Low contrast
            (240, 217, 181), # Light square
            (181, 136, 99),  # Dark square
            (50, 50, 50)     # Background
        ),
        "high": (   # High contrast
            (255, 235, 200),
            (120, 80, 40),
            (20, 20, 20)
        )
    },
    "gray": {
        "low": (
            (220, 220, 220),
            (100, 100, 100),
            (30, 30, 30)
        ),
        "high": (
            (255, 255, 255),
            (0, 0, 0),
            (10, 10, 10)
        )
    },
    "blue": {
        "low": (
            (200, 220, 240),
            (80, 100, 140),
            (20, 30, 50)
        ),
        "high": (
            (230, 245, 255),
            (40, 60, 120),
            (10, 20, 40)
        )
    },
    "green": {
        "low": (
            (210, 230, 200),
            (80, 120, 90),
            (40, 60, 50)
        ),
        "high": (
            (235, 255, 220),
            (40, 80, 50),
            (20, 40, 30)
        )
    },
    "red": {
        "low": (
            (240, 200, 200),
            (140, 60, 60),
            (40, 20, 10)
        ),
        "high": (
            (255, 220, 220),
            (100, 30, 30),
            (30, 10, 10)
        )
    },
    "purple": {
        "low": (
            (230, 210, 240),
            (80, 50, 100),
            (40, 30, 50)
        ),
        "high": (
            (250, 230, 255),
            (60, 30, 100),
            (20, 10, 30)
        )
    },
    "orange": {
        "low": (
            (250, 220, 180),
            (180, 100, 40),
            (60, 40, 20)
        ),
        "high": (
            (255, 240, 200),
            (140, 60, 20),
            (30, 20, 10)
        )
    },
    "yellow": {
        "low": (
            (255, 250, 200),
            (180, 160, 60),
            (70, 70, 40)
        ),
        "high": (
            (255, 255, 180),
            (140, 120, 20),
            (40, 40, 20)
        )
    },
    "teal": {
        "low": (
            (200, 240, 230),
            (60, 120, 110),
            (30, 60, 50)
        ),
        "high": (
            (220, 255, 245),
            (30, 80, 70),
            (15, 30, 25)
        )
    },
    "pink": {
        "low": (
            (245, 220, 230),
            (180, 100, 130),
            (60, 40, 50)
        ),
        "high": (
            (255, 235, 245),
            (140, 60, 90),
            (30, 20, 30)
        )
    },
    "sand": {
        "low": (
            (245, 235, 220),
            (180, 160, 130),
            (60, 50, 40)
        ),
        "high": (
            (255, 245, 230),
            (140, 120, 90),
            (30, 25, 20)
        )
    },
    "minimal": {
        "low": (
            (255, 255, 255),
            (0, 0, 0),
            (20, 20, 20)
        ),
        "high": (
            (255, 255, 255),
            (0, 0, 0),
            (0, 0, 0)
        )
    }
}


HIGHLIGHT_COLORS = (
    (60, 120, 180),   
    (255, 100, 100),  
    (50, 180, 160),   
    (180, 60, 60),    
    (60, 120, 180),   
    (180, 255, 180),
    (60, 180, 255),
    (120, 180, 255),
    (255, 180, 60),   
    (60, 180, 255),
    (100, 160, 220),  
    (255, 0, 255),     

)
