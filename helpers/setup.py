from typing import Optional
from helpers.parse_fen import parse_fen

def setup_from_fen(fen: str, board, gamestate, square_size):
    parsed = parse_fen(fen, square_size)

    board.grid = parsed['grid']
    board.en_passant_target = parsed['en_passant_target']
    board.update_castling_rights(parsed['castling_rights'])
    board.king_positions = find_kings(board.grid)

    gamestate.turn = parsed['turn']
    gamestate.castling_rights = parsed['castling_rights']
    gamestate.halfmove_clock = parsed['halfmove_clock']
    gamestate.fullmove_number = parsed['fullmove_number']


def find_kings(grid):
    positions: dict[str, Optional[tuple[int, int]]] = {'w': None, 'b': None}
    for r in range(8):
        for c in range(8):
            piece = grid[r][c]
            if piece and piece.type == 'k':
                positions[piece.color] = (r, c)
    return positions
##