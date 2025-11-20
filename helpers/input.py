from config import SQUARE_SIZE, BOARD_ORIGIN_X, BOARD_ORIGIN_Y
import pygame

def detect_promotion_click(pos, base_row, base_col, color):
    x, y = pos
    col_px = BOARD_ORIGIN_X + base_col * SQUARE_SIZE

    for i, piece_type in enumerate(['q', 'r', 'n', 'b']):
        if color == 'w':
            # White: choices drawn below the promotion square
            row_px = BOARD_ORIGIN_Y + base_row * SQUARE_SIZE + i * SQUARE_SIZE
        else:
            # Black: choices drawn above the promotion square
            row_px = BOARD_ORIGIN_Y + base_row * SQUARE_SIZE - (i + 1) * SQUARE_SIZE

        rect = pygame.Rect(col_px, row_px, SQUARE_SIZE, SQUARE_SIZE)
        if rect.collidepoint(x, y):
            return piece_type
    return None
