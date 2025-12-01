from move import Move
import constants as C

def generate_pawn_moves(board, square):
    moves = []
    rank = square // 8
    file = square %  8

    direction  = C.UP if board.turn == 1 else C.DOWN
    start_rank = C.WHITE_PAWN_START_RANK if board.turn == 1 else C.BLACK_PAWN_START_RANK

    forward_one = square + direction
    if 0 <= forward_one < 64 and board.squares[forward_one] == C.EMPTY:
        # check for promotion
        rank = forward_one // 8
        if (board.turn == 1 and rank == C.WHITE_PROMOTION_RANK) or \
            (board.turn == -1 and rank == C.BLACK_PROMOTION_RANK):
            moves.extend(generate_promotion_moves(board, square, forward_one, is_capture=False))
        else:
            moves.append(Move.encode_move(square, forward_one))
        
        if (square // 8) == start_rank:
            forward_two = forward_one + direction
            if 0 <= forward_two < 64 and board.squares[forward_two] == C.EMPTY:
                moves.append(Move.encode_move(square, forward_two))

    # captures
    for capture_dir in [direction + C.LEFT, direction + C.RIGHT]:
        capture_square = square + capture_dir

        if not (0 <= capture_square < 64):
            continue
        
        capture_file = capture_square %  8

        if abs(capture_file - file) > 1:
            continue
        
        target = board.squares[capture_square]

        if target != C.EMPTY and board.turn * target < 0:
            capture_rank = capture_square // 8
            if (board.turn == 1 and capture_rank == C.WHITE_PROMOTION_RANK) or \
               (board.turn == -1 and capture_rank == C.BLACK_PROMOTION_RANK):
                moves.extend(generate_promotion_moves(board, square, capture_square, is_capture=True))

            else:
                moves.append(Move.encode_move(square, capture_square, C.CAPTURE))

        elif capture_square == board.en_passant and board.enpassant_available():
            moves.append(Move.encode_move(square, capture_square, C.EN_PASSANT))
    
    return moves

def generate_knight_moves(board, square):
    # pseudo legal knight moves
    moves = []

    rank = square // 8
    file = square %  8

    for offset in C.KNIGHT_DIRS:
        new_square = square + offset

        if not (0 <= new_square < 64): # out of bounds
            continue
        
        new_rank = new_square // 8
        new_file = new_square %  8

        if abs(new_rank - rank) > 2 or abs(new_file - file) > 2:
            continue
        
        target_piece = board.squares[new_square]
        if target_piece == C.EMPTY:
            moves.append(Move.encode_move(square, new_square))
        elif target_piece * board.turn < 0:
            moves.append(Move.encode_move(square, new_square, C.CAPTURE))

    return moves

def generate_bishop_moves(board, square):
    return generate_sliding_moves(board, square)

def generate_rook_moves(board, square):
    return generate_sliding_moves(board, square)

def generate_queen_moves(board, square):
    return generate_sliding_moves(board, square)

def generate_sliding_moves(board, square):
    type_dirs = {
        3: C.BISHOP_DIRS,
        4: C.ROOK_DIRS,
        5: C.QUEEN_DIRS
    }
    moves = []

    piece_type = abs(board.squares[square])
    directions = type_dirs.get(piece_type)
    if directions is None:
        return []

    for direction in directions:
        current = square + direction

        while 0 <= current < 64:
            current_file = current %  8


            prev = current - direction
            if abs((current % 8) - (prev % 8)) != 1 and direction in (C.LEFT, C.RIGHT, C.UP_LEFT, C.UP_RIGHT, C.DOWN_LEFT, C.DOWN_RIGHT):
                break

            target = board.squares[current]

            if target == C.EMPTY: # square is empty
                moves.append(Move.encode_move(square, current))
                current += direction
            elif target * board.turn < 0: # enemy piece
                moves.append(Move.encode_move(square, current, C.CAPTURE))
                break
            else:    # friendly piece
                break
    return moves

def generate_king_moves(board, square):
    moves = []
    rank = square // 8
    file = square %  8

    # normal moves
    for direction in C.KING_DIRS:
        new_square = square + direction
        
        if not (0 <= new_square < 64):
            continue
        
        new_rank = new_square // 8
        new_file = new_square %  8
        if abs(new_file - file) > 1 or abs(new_rank - rank) > 1:
            continue
        
        target = board.squares[new_square]
        if not board._is_square_attacked(new_square, -board.turn):
            if target == C.EMPTY:
                moves.append(Move.encode_move(square, new_square))
            elif target * board.turn < 0:
                moves.append(Move.encode_move(square, new_square, C.CAPTURE))

    # castling moves
    if board.turn == 1: # white
        # kingside 
        if (board.white_king_pos == C.WHITE_KING_START and (board.castling & C.CASTLE_WK) and
            not board.is_in_check(1) and
            all(board.squares[sq] == C.EMPTY for sq in C.WHITE_KINGSIDE_PATH) and
            all(not board._is_square_attacked(sq, -1) for sq in [C.WHITE_KING_START] + C.WHITE_KINGSIDE_PATH) and
            board.squares[C.WHITE_ROOK_H1] == C.W_ROOK):
            moves.append(Move.encode_move(C.WHITE_KING_START, C.WHITE_KINGSIDE_CASTLE, C.CASTLING))
        
        # queenside
        if (board.white_king_pos == C.WHITE_KING_START and (board.castling & C.CASTLE_WQ) and
            not board.is_in_check(1) and
            all(board.squares[sq] == C.EMPTY for sq in C.WHITE_QUEENSIDE_PATH) and
            all(not board._is_square_attacked(sq, -1) for sq in [C.WHITE_KING_START] + C.WHITE_QUEENSIDE_PATH) and
            board.squares[C.WHITE_ROOK_A1] == C.W_ROOK):
            moves.append(Move.encode_move(C.WHITE_KING_START, C.WHITE_QUEENSIDE_CASTLE, C.CASTLING))

    else: # black
        if (board.black_king_pos == C.BLACK_KING_START and (board.castling & C.CASTLE_BK) and
            not board.is_in_check(-1) and
            all(board.squares[sq] == C.EMPTY for sq in C.BLACK_KINGSIDE_PATH) and
            all(not board._is_square_attacked(sq, 1) for sq in [C.BLACK_KING_START] + C.BLACK_KINGSIDE_PATH) and
            board.squares[C.BLACK_ROOK_H8] == C.B_ROOK):
            moves.append(Move.encode_move(C.BLACK_KING_START, C.BLACK_KINGSIDE_CASTLE, C.CASTLING))
        
        # queenside
        if (board.black_king_pos == C.BLACK_KING_START and (board.castling & C.CASTLE_BQ) and
            not board.is_in_check(-1) and
            all(board.squares[sq] == C.EMPTY for sq in C.BLACK_QUEENSIDE_PATH) and
            all(not board._is_square_attacked(sq, 1) for sq in [C.BLACK_KING_START] + C.BLACK_QUEENSIDE_PATH) and
            board.squares[C.BLACK_ROOK_A8] == C.B_ROOK):
            moves.append(Move.encode_move(C.BLACK_KING_START, C.BLACK_QUEENSIDE_CASTLE, C.CASTLING))
        
    return moves

def generate_promotion_moves(board, from_sq, to_sq, is_capture=False):
    moves = []
    if is_capture:
        moves.append(Move.encode_move(from_sq, to_sq, C.PROMOTION_QUEEN_CAPTURE))
        moves.append(Move.encode_move(from_sq, to_sq, C.PROMOTION_ROOK_CAPTURE))
        moves.append(Move.encode_move(from_sq, to_sq, C.PROMOTION_BISHOP_CAPTURE))
        moves.append(Move.encode_move(from_sq, to_sq, C.PROMOTION_KNIGHT_CAPTURE))
    else:
        moves.append(Move.encode_move(from_sq, to_sq, C.PROMOTION_QUEEN))
        moves.append(Move.encode_move(from_sq, to_sq, C.PROMOTION_ROOK))
        moves.append(Move.encode_move(from_sq, to_sq, C.PROMOTION_BISHOP))
        moves.append(Move.encode_move(from_sq, to_sq, C.PROMOTION_KNIGHT))
    return moves
