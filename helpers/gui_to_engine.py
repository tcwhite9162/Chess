import engine.constants as C

def convert_gui_to_engine(gui_board, engine_board, turn):
    for row in range(8):
        for col in range(8):
            piece = gui_board.grid[row][col]
            idx = row * 8 + col
            if piece is None:
                engine_board.squares[idx] = C.EMPTY
            else:
                if piece.color == 'w':
                    if piece.type == 'p': engine_board.squares[idx] = C.W_PAWN
                    elif piece.type == 'n': engine_board.squares[idx] = C.W_KNIGHT
                    elif piece.type == 'b': engine_board.squares[idx] = C.W_BISHOP
                    elif piece.type == 'r': engine_board.squares[idx] = C.W_ROOK
                    elif piece.type == 'q': engine_board.squares[idx] = C.W_QUEEN
                    elif piece.type == 'k': engine_board.squares[idx] = C.W_KING
                else:
                    if piece.type == 'p': engine_board.squares[idx] = C.B_PAWN
                    elif piece.type == 'n': engine_board.squares[idx] = C.B_KNIGHT
                    elif piece.type == 'b': engine_board.squares[idx] = C.B_BISHOP
                    elif piece.type == 'r': engine_board.squares[idx] = C.B_ROOK
                    elif piece.type == 'q': engine_board.squares[idx] = C.B_QUEEN
                    elif piece.type == 'k': engine_board.squares[idx] = C.B_KING

    # Sync turn
    engine_board.turn = 1 if turn == 'w' else -1
    # Sync castling rights and en passant if needed
    engine_board.castling_rights = gui_board._castling_rights
    engine_board.en_passant_target = (
        gui_board.en_passant_target[0] * 8 + gui_board.en_passant_target[1]
        if gui_board.en_passant_target else None
    )

def convert_engine_move_to_gui(move):
    from_sq = move & 0x3F
    to_sq   = (move >> 6) & 0x3F
    start = (from_sq // 8, from_sq % 8)
    end   = (to_sq // 8, to_sq % 8)
    return start, end
