from engine.EngineBoard import Board
import engine.constants as C

def negamax(board, depth, alpha, beta):
    if depth == 0 or board.is_terminal():
        return board.evaluate()

    max_value = -float("inf")
    for move in board.generate_legal_moves():
        board.make_move(move)
        value = -negamax(board, depth - 1, -beta, -alpha)
        board.unmake_move()

        max_value = max(max_value, value)
        alpha = max(alpha, value)
        if alpha > beta:
            break

    return max_value

def search_best_move(board, depth):
    best_score = -float('inf')
    best_move = None

    for move in board.generate_legal_moves():
        board.make_move(move)
        score = -negamax(board, depth - 1, -float('inf'), float('inf'))
        board.unmake_move()

        if score > best_score:
            best_score = score
            best_move = move

    return best_move, best_score
