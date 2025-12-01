from eval_config import PST_MAP, PIECE_VALUES, MOBILITY_FACTOR, PAWN_PENALTY
import constants as C

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

    white_score = material + pst_sum + mobility_score + pawn_score

    return white_score * board.turn
