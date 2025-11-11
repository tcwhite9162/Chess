from config import SQUARE_SIZE, BOARD_ORIGIN_X, BOARD_ORIGIN_Y, RADIUS, CAPTURE_RING_WIDTH, CHECK_BORDER_WIDTH, FONT_SIZE, FONT_COLOR, OVERLAY_COLOR, SCREEN_HEIGHT, SCREEN_WIDTH
from game.piece import Piece
import pygame

# light_square, dark_square, background = COLOR_PALETTES["red"]["low"]
def render_board(window, board, gamestate):
    light_square, dark_square, background, highlight = gamestate.active_colors()
    window.fill(background)
    legal_moves, captures = gamestate.available_moves, gamestate.available_captures

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

    render_legal_moves(window, legal_moves, highlight)
    render_captures(window, captures, highlight)
    
    in_check = board.check_pos(gamestate.turn)
    if in_check:
        render_check(window, *in_check)

    for row in range(board.rows):
        for col in range(board.cols):
            if board.grid[row][col] is not None:
                render_piece(window, board, row, col)

    if gamestate.awaiting_promotion:
        row, col, color = gamestate.awaiting_promotion
        render_promotion_choices(window, row, col, color)

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

def render_check(window, row, col, color=(255,0,0)):
    x = BOARD_ORIGIN_X + col * SQUARE_SIZE
    y = BOARD_ORIGIN_Y + row * SQUARE_SIZE
    pygame.draw.rect(window, color, (x, y, SQUARE_SIZE, SQUARE_SIZE), width=CHECK_BORDER_WIDTH)

def render_captures(window, captures, color):
    color = scale_color(color, (1.5, 1.2, 1))
    
    for row, col in captures:
        x = BOARD_ORIGIN_X + col * SQUARE_SIZE + SQUARE_SIZE // 2 # Center of square
        y = BOARD_ORIGIN_Y + row * SQUARE_SIZE + SQUARE_SIZE // 2

        pygame.draw.circle(window, color, (x, y), SQUARE_SIZE // 2, width=CAPTURE_RING_WIDTH)

def render_promotion_choices(window, row, col, color):
    square_color = (50, 50, 50) if color == 'w' else (220, 220, 220)
    print("Rendering promotion")
    choices = ['q', 'r', 'n', 'b']
    for i, piece_type in enumerate(choices):
        x = BOARD_ORIGIN_X + col * SQUARE_SIZE

        if color == 'w':
            y = BOARD_ORIGIN_Y + row * SQUARE_SIZE + i * SQUARE_SIZE
        else:
            y = BOARD_ORIGIN_Y + row * SQUARE_SIZE - (i + 1) * SQUARE_SIZE

        pygame.draw.rect(window, square_color, (x, y, SQUARE_SIZE, SQUARE_SIZE))
        piece = Piece(color, piece_type, SQUARE_SIZE)
        window.blit(piece.image, (x, y))

def scale_color(color, factor):
    r, g, b    = color
    rf, gf, bf = factor
    
    return (min(255, r * rf), min(255, g * gf), min(255, b * bf))


def render_gameover(window, board, gamestate):
    render_board(window, board, gamestate)

    overlay_width = SQUARE_SIZE * 5.6
    overlay_height = SQUARE_SIZE * 1.8
    
    # Center the overlay on the board
    overlay_x = BOARD_ORIGIN_X + (SQUARE_SIZE * 8 - overlay_width) // 2
    overlay_y = BOARD_ORIGIN_Y + (SQUARE_SIZE * 8 - overlay_height) // 2
    
    # Create transparent surface and draw rounded rect on it
    overlay = pygame.Surface((overlay_width, overlay_height), pygame.SRCALPHA)
    pygame.draw.rect(overlay, OVERLAY_COLOR, (0, 0, overlay_width, overlay_height), border_radius=15)
    window.blit(overlay, (overlay_x, overlay_y))
    
    if gamestate.is_checkmate:
        message = f"Checkmate, {gamestate.winner} Wins"
    elif gamestate.is_stalemate:
        message = "Stalemate, Draw"
    else:
        message = "Game Over ??? how"
    
    # Draw message 
    font = pygame.font.SysFont("arial", FONT_SIZE)
    text_surface = font.render(message, True, FONT_COLOR)
    text_rect = text_surface.get_rect(center=(overlay_x + overlay_width // 2, 
                                               overlay_y + overlay_height // 2))
    window.blit(text_surface, text_rect)