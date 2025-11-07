from config import SQUARE_SIZE, BOARD_ORIGIN_X, BOARD_ORIGIN_Y, RADIUS
import pygame

# light_square, dark_square, background = COLOR_PALETTES["red"]["low"]
def render_board(window, board, gamestate):
    light_square, dark_square, background, highlight = gamestate.current_colors()
    window.fill(background)

    for row in range(board.rows):
        for col in range(board.cols):
            if (row + col) % 2 != 0:
                color = dark_square
            else:
                color = light_square

            x = BOARD_ORIGIN_X + col * SQUARE_SIZE
            y = BOARD_ORIGIN_Y + row * SQUARE_SIZE
            pygame.draw.rect(window, color, (x, y, SQUARE_SIZE, SQUARE_SIZE))

            if gamestate.selected_square == (row, col):
                pygame.draw.rect(window, highlight, (x, y, SQUARE_SIZE, SQUARE_SIZE))
            
            if board.grid[row][col] is not None:
                render_piece(window, board, row, col)

    render_legal_moves(window, gamestate.legal_moves, highlight)

def render_piece(window, board, row, col):
    piece = board.grid[row][col]
    x = BOARD_ORIGIN_X + col * SQUARE_SIZE
    y = BOARD_ORIGIN_Y + row * SQUARE_SIZE
    window.blit(piece.image, (x, y))

def render_legal_moves(window, moves, color):
    color = scale_color(color, (0.2, 0.1, 0.5))

    for row, col in moves:
        x = BOARD_ORIGIN_X + col * SQUARE_SIZE + SQUARE_SIZE // 2 # Center of square
        y = BOARD_ORIGIN_Y + row * SQUARE_SIZE + SQUARE_SIZE // 2
        pygame.draw.circle(window, color, (x, y), SQUARE_SIZE // RADIUS)

def scale_color(color, factor):
    r, g, b    = color
    rf, gf, bf = factor
    
    return (min(255, r * rf) + 1, min(255, g * gf) + 1, min(255, b * bf) + 1)