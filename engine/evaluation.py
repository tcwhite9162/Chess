from engine.eval_config import PST_MAP, PIECE_VALUES, MOBILITY_FACTOR, PAWN_PENALTY
import engine.constants as C

mirror_square = lambda x: 63 - x

def pst_value(piece, square):
    table = PST_MAP.get(abs(piece))
    if table is None:
        return 0
    if piece > 0:
        return table[square]
    else:
        return -table[mirror_square(square)]

def evaluate(board):
    material = 0
    pst_sum  = 0

    for square, piece in enumerate(board.squares):
        if piece == C.EMPTY:
            continue

        val = PIECE_VALUES[abs(piece)]
        material += val if piece > 0 else -val
        pst_sum  += pst_value(piece, square)

    my_moves = board.count_pseudo_moves_for_side(board.turn)
    opp_moves = board.count_pseudo_moves_for_side(-board.turn)

    mobility_score = MOBILITY_FACTOR * (my_moves - opp_moves)

    pawn_score = 0
    files = [0]*8
    files_black = [0]*8

    for square, piece in enumerate(board.squares):
        if piece == C.W_PAWN:
            file = square % 8
            files[file] += 1
        elif piece == C.B_PAWN:
            file = square % 8
            files_black[file] += 1

    for f in range(8):
        if files[f] > 1:
            pawn_score -= PAWN_PENALTY * (files[f] - 1)
        if files_black[f] > 1:
            pawn_score += PAWN_PENALTY * (files_black[f] - 1)

    white_score = material + pst_sum + mobility_score + pawn_score + king_safety(board)

    return white_score * board.turn

def king_safety(board):
    score = 0
    
    wk = board.white_king_pos
    wk_file = wk % 8
    wk_rank = wk // 8

    if wk in (C.WHITE_KINGSIDE_CASTLE, C.WHITE_QUEENSIDE_CASTLE):
        score += 40
    elif wk == C.WHITE_KING_START:
        score -= 20

    if wk_rank == 7:
        for df in (-1, 0, 1):
            f = wk_file + df
            if 0 <= f < 8:
                square = (wk_rank - 1) * 8 + f
                if board.squares[square] == C.W_PAWN:
                    score += 10
                else:
                    score -= 10
    
    bk = board.black_king_pos
    bk_file = bk % 8
    bk_rank = bk // 8

    if bk in (C.BLACK_KINGSIDE_CASTLE, C.BLACK_QUEENSIDE_CASTLE):
        score -= 40
    elif bk == C.BLACK_KING_START:
        score += 20

    if bk_rank == 0:  # king on starting rank
        for df in (-1, 0, 1):
            f = bk_file + df
            if 0 <= f < 8:
                sq = (bk_rank + 1) * 8 + f
                if board.squares[sq] == C.B_PAWN:
                    score -= 10
                else:
                    score += 10

    return score