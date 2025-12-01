
import pytest
from EngineBoard import Board
from move import Move
from constants import *

def square_to_coord(square):
    files = "abcdefgh"
    file = square % 8
    rank = square // 8
    return files[file] + str(8 - rank)

def decode_move(move):
    from_sq = move & 0x3F
    to_sq   = (move >> 6) & 0x3F
    flags   = (move >> 12) & 0xF

    from_coord = square_to_coord(from_sq)
    to_coord   = square_to_coord(to_sq)

    if flags == CASTLING:
        if to_coord in ("g1", "g8"):
            return "O-O"
        elif to_coord in ("c1", "c8"):
            return "O-O-O"

    promo_map = {
        PROMOTION_QUEEN: "Q",
        PROMOTION_ROOK: "R",
        PROMOTION_BISHOP: "B",
        PROMOTION_KNIGHT: "N",
        PROMOTION_QUEEN_CAPTURE: "Q",
        PROMOTION_ROOK_CAPTURE: "R",
        PROMOTION_BISHOP_CAPTURE: "B",
        PROMOTION_KNIGHT_CAPTURE: "N",
    }
    if flags in promo_map:
        return f"{from_coord}{to_coord}{promo_map[flags]}"

    if flags == EN_PASSANT:
        return f"{from_coord}x{to_coord} e.p."

    if flags & CAPTURE:
        return f"{from_coord}x{to_coord}"

    return f"{from_coord}{to_coord}"

def coord_to_square(coord: str) -> int:
    files = "abcdefgh"
    file = files.index(coord[0])
    rank = int(coord[1])
    return (8 - rank) * 8 + file


def test_promotion():
    board = Board()
    board.setup_starting_position()
    board.squares[52] = EMPTY
    board.squares[12] = W_PAWN
    move = Move.encode_move(12, 4, PROMOTION_QUEEN)
    board.make_move(move)
    assert board.squares[4] == W_QUEEN
    board.unmake_move()
    assert board.squares[12] == W_PAWN


def test_en_passant():
    board = Board()
    board.setup_starting_position()
    board.squares[52] = EMPTY
    board.squares[36] = W_PAWN
    board.squares[35] = B_PAWN
    board.turn = -1
    board.en_passant = 44
    move = Move.encode_move(35, 44, EN_PASSANT)
    board.make_move(move)
    assert board.squares[44] == B_PAWN
    assert board.squares[36] == EMPTY
    board.unmake_move()
    assert board.squares[35] == B_PAWN
    assert board.squares[36] == W_PAWN


def test_castling():
    board = Board()
    board.setup_starting_position()
    board.squares[61] = EMPTY
    board.squares[62] = EMPTY
    move = Move.encode_move(60, 62, CASTLING)
    board.make_move(move)
    assert board.squares[62] == W_KING
    assert board.squares[61] == W_ROOK
    board.unmake_move()
    assert board.squares[60] == W_KING
    assert board.squares[63] == W_ROOK


def test_is_square_attacked():
    board = Board()
    board.squares = [EMPTY] * 64
    board.squares[48] = W_PAWN
    assert board._is_square_attacked(41, 1)
    assert not board._is_square_attacked(39, 1)

    board.squares = [EMPTY] * 64
    board.squares[15] = B_PAWN
    assert board._is_square_attacked(22, -1)
    assert not board._is_square_attacked(16, -1)

    board.squares = [EMPTY] * 64
    board.squares[56] = W_KNIGHT
    assert board._is_square_attacked(41, 1)
    assert board._is_square_attacked(50, 1)
    assert not board._is_square_attacked(39, 1)


def test_generate_legal_moves():
    board = Board()
    board.squares = [EMPTY] * 64
    board.squares[60] = W_KING; board.white_king_pos = 60
    board.squares[4] = B_ROOK;  board.black_king_pos = 0
    board.turn = 1
    moves1 = board.generate_legal_moves()
    assert len(moves1) > 0

    board.squares = [EMPTY] * 64
    board.squares[60] = W_KING; board.white_king_pos = 60
    board.squares[0] = B_ROOK;  board.black_king_pos = 4
    board.turn = 1
    moves2 = board.generate_legal_moves()
    assert len(moves2) >= len(moves1)

    board.squares = [EMPTY] * 64
    board.squares[63] = W_KING; board.white_king_pos = 63
    board.squares[62] = B_ROOK
    board.squares[55] = B_ROOK
    board.squares[54] = B_KING; board.black_king_pos = 54
    board.turn = 1
    moves3 = board.generate_legal_moves()
    assert moves3 == []

def test_starting_position_has_20_moves():
    board = Board()
    board.setup_starting_position()
    board.turn = 1  # White to move
    moves = board.generate_legal_moves()
    assert len(moves) == 20, f"Expected 20 moves, got {len(moves)}"


def test_fools_mate_checkmate():
    board = Board()
    board.setup_starting_position()

    # 1. f3
    move_f3 = Move.encode_move(53, 45)  # f2 -> f3
    board.make_move(move_f3)

    # ... e5
    move_e5 = Move.encode_move(12, 28)  # e7 -> e5
    board.make_move(move_e5)

    # 2. g4
    move_g4 = Move.encode_move(54, 38)  # g2 -> g4
    board.make_move(move_g4)

    # ... Qh4#
    move_qh4 = Move.encode_move(3, 39)  # d8 -> h4
    board.make_move(move_qh4)

    assert board.is_checkmate(), "Expected checkmate after Qh4#"


# === Edge Wrapping Tests ===
def test_rook_no_wrap_horizontal():
    """Rook on h-file shouldn't wrap to a-file"""
    board = Board()
    board.squares = [EMPTY] * 64
    board.squares[7] = W_ROOK  # h8
    board.squares[4] = W_KING
    board.white_king_pos = 4
    board.squares[60] = B_KING
    board.black_king_pos = 60
    board.turn = 1
    
    moves = board.generate_pseudo_legal_moves()
    move_coords = [decode_move(m) for m in moves if (m & 0x3F) == 7]
    
    # Rook should not be able to move to a8 (square 0)
    assert "h8a8" not in move_coords, "Rook wrapped from h-file to a-file"
    assert "h8g8" in move_coords, "Rook should move left on h-file"

def test_queen_edge_of_board():
    """Queen on edge squares shouldn't wrap"""
    board = Board()
    board.squares = [EMPTY] * 64
    board.squares[0] = W_QUEEN  # a8
    board.squares[60] = W_KING
    board.white_king_pos = 60
    board.squares[4] = B_KING
    board.black_king_pos = 4
    board.turn = 1
    
    moves = board.generate_pseudo_legal_moves()
    move_coords = [decode_move(m) for m in moves if (m & 0x3F) == 0]
    
    # Queen on a8 should not be able to reach h-file horizontally via wrapping
    for move in move_coords:
        if move.startswith("a8"):
            to_square = move[2:4]
            to_file = to_square[0]
            # If moving horizontally (same rank), shouldn't wrap
            if to_square[1] == '8' and to_file == 'h':
                # Check if there's a valid path
                from_sq = 0  # a8
                to_sq = coord_to_square(to_square)
                # Path from a8 to h8 should go through b8, c8, etc.
                assert to_file != 'h' or any(board.squares[i] == EMPTY for i in range(1, 7)), \
                    "Queen wrapped horizontally"


# === Pin Tests ===
def test_pinned_piece_cannot_move():
    """Piece pinned to king cannot move"""
    board = Board()
    board.squares = [EMPTY] * 64
    board.squares[60] = W_KING  # e1
    board.white_king_pos = 60
    board.squares[52] = W_BISHOP  # e2
    board.squares[44] = B_ROOK  # e3
    board.squares[4] = B_KING
    board.black_king_pos = 4
    board.turn = 1
    
    moves = board.generate_legal_moves()
    bishop_moves = [m for m in moves if (m & 0x3F) == 52]
    
    # Bishop is pinned, can only move along the e-file or capture the rook
    assert len(bishop_moves) == 0, "Pinned bishop should not be able to move diagonally"

def test_pinned_piece_can_capture_attacker():
    """Pinned piece can capture the attacker"""
    board = Board()
    board.squares = [EMPTY] * 64
    board.squares[60] = W_KING  # e1
    board.white_king_pos = 60
    board.squares[52] = W_ROOK  # e2
    board.squares[44] = B_ROOK  # e3
    board.squares[4] = B_KING
    board.black_king_pos = 4
    board.turn = 1
    
    moves = board.generate_legal_moves()
    rook_moves = [decode_move(m) for m in moves if (m & 0x3F) == 52]
    
    # Rook can capture the attacking rook
    assert "e2xe3" in rook_moves, "Pinned rook should be able to capture attacker"


def test_must_block_check():
    """When in check, must block or move king"""
    board = Board()
    board.squares = [EMPTY] * 64
    board.squares[60] = W_KING  # e1
    board.white_king_pos = 60
    board.squares[55] = W_BISHOP  # h2 (can't help)
    board.squares[52] = B_ROOK  # e2
    board.squares[4] = B_KING
    board.black_king_pos = 4
    board.turn = 1

def test_cannot_move_into_check():
    """King cannot move into check"""
    board = Board()
    board.squares = [EMPTY] * 64
    board.squares[60] = W_KING  # e1
    board.white_king_pos = 60
    board.squares[43] = B_ROOK  # d3
    board.squares[4] = B_KING
    board.black_king_pos = 4
    board.turn = 1
    
    moves = board.generate_legal_moves()
    move_coords = [decode_move(m) for m in moves]
    
    # King cannot move to d1, d2 (under attack by rook)
    assert "e1d1" not in move_coords, "King moved into check (d1)"
    assert "e1d2" not in move_coords, "King moved into check (d2)"

def test_castling_rights_lost_after_king_move():
    """Castling rights lost after king moves"""
    board = Board()
    board.setup_starting_position()
    board.squares[61] = EMPTY
    board.squares[62] = EMPTY
    
    # Move king and back
    king_move = Move.encode_move(60, 61)
    board.make_move(king_move)
    assert (board.castling & 0b0011) == 0, "White lost castling rights"
    
    board.make_move(Move.encode_move(8, 16))  # Black pawn
    
    king_move_back = Move.encode_move(61, 60)
    board.make_move(king_move_back)
    
    moves = board.generate_legal_moves()
    move_coords = [decode_move(m) for m in moves]
    
    assert "O-O" not in move_coords, "Cannot castle after king moved"

def test_castling_rights_lost_after_rook_move():
    """Castling rights lost after rook moves"""
    board = Board()
    board.setup_starting_position()
    board.squares[61] = EMPTY
    board.squares[62] = EMPTY
    
    # Move h1 rook
    rook_move = Move.encode_move(63, 62)
    board.make_move(rook_move)
    
    assert (board.castling & 0b0001) == 0, "Kingside castling right lost"
    assert (board.castling & 0b0010) != 0, "Queenside castling right should remain"


# === En Passant Tests ===
def test_en_passant_capture():
    """En passant capture works correctly"""
    board = Board()
    board.squares = [EMPTY] * 64
    board.squares[60] = W_KING
    board.white_king_pos = 60
    board.squares[4] = B_KING
    board.black_king_pos = 4
    board.squares[24] = W_PAWN  # a5
    board.squares[9] = B_PAWN   # b7
    board.turn = -1
    
    # Black pawn moves two squares
    move = Move.encode_move(9, 25)  # b7 to b5
    board.make_move(move)
    
    assert board.en_passant == 17, "En passant square should be b6"
    
    # White can capture en passant
    moves = board.generate_legal_moves()
    move_coords = [decode_move(m) for m in moves]
    
    assert any("a5xb6 e.p." in m for m in move_coords), "En passant capture should be available"

def test_en_passant_expires():
    """En passant opportunity expires after one move"""
    board = Board()
    board.squares = [EMPTY] * 64
    board.squares[60] = W_KING
    board.white_king_pos = 60
    board.squares[4] = B_KING
    board.black_king_pos = 4
    board.squares[24] = W_PAWN  # a5
    board.squares[9] = B_PAWN   # b7
    board.squares[48] = W_PAWN  # a2
    board.turn = -1
    
    # Black pawn moves two squares
    board.make_move(Move.encode_move(9, 25))  # b7 to b5
    
    # White makes different move
    board.make_move(Move.encode_move(48, 40))  # a2 to a3
    
    # Black moves
    board.make_move(Move.encode_move(8, 16))  # a7 to a6
    
    # En passant should no longer be available
    moves = board.generate_legal_moves()
    move_coords = [decode_move(m) for m in moves]
    
    assert not any("e.p." in m for m in move_coords), "En passant should have expired"


# === Promotion Tests ===
def test_promotion_all_pieces():
    """Can promote to all piece types"""
    board = Board()
    board.squares = [EMPTY] * 64
    board.squares[60] = W_KING
    board.white_king_pos = 60
    board.squares[4] = B_KING
    board.black_king_pos = 4
    board.squares[8] = W_PAWN  # a7
    board.turn = 1
    
    moves = board.generate_legal_moves()
    move_coords = [decode_move(m) for m in moves]
    
    promotion_moves = [m for m in move_coords if m.startswith("a7a8")]
    
    assert "a7a8Q" in promotion_moves, "Should be able to promote to Queen"
    assert "a7a8R" in promotion_moves, "Should be able to promote to Rook"
    assert "a7a8B" in promotion_moves, "Should be able to promote to Bishop"
    assert "a7a8N" in promotion_moves, "Should be able to promote to Knight"

def test_promotion_with_capture():
    """Promotion with capture works"""
    board = Board()
    board.squares = [EMPTY] * 64
    board.squares[60] = W_KING
    board.white_king_pos = 60
    board.squares[4] = B_KING
    board.black_king_pos = 4
    board.squares[8] = W_PAWN  # a7
    board.squares[1] = B_ROOK  # b8
    board.turn = 1
    
    moves = board.generate_legal_moves()
    move_coords = [decode_move(m) for m in moves]
    
    capture_promotions = [m for m in move_coords if m.startswith("a7") and "b8" in m]
    
    assert len(capture_promotions) == 4, "Should have 4 capture promotion options"


# === Stalemate Tests ===
def test_stalemate():
    """Detect stalemate correctly"""
    board = Board()
    board.squares = [EMPTY] * 64
    # Classic stalemate: White king in corner, black king and queen trap it
    board.squares[0] = W_KING   # a8
    board.white_king_pos = 0
    board.squares[18] = B_KING  # c6 
    board.black_king_pos = 18
    board.squares[10] = B_QUEEN # c7
    board.turn = 1
    
    # White king at a8 has no legal moves:
    # - a7: attacked by queen at c7
    # - b8: attacked by queen at c7
    # - b7: attacked by queen at c7
    # But not currently in check
    
    assert not board.is_in_check(1), "White should not be in check"
    assert board.is_stalemate(), "Should be stalemate"
    assert not board.is_checkmate(), "Should not be checkmate"


# === Move/Unmake Tests ===
def test_make_unmake_preserves_state():
    """Making and unmaking moves preserves board state"""
    board = Board()
    board.setup_starting_position()
    
    # Save initial state
    initial_squares = board.squares.copy()
    initial_turn = board.turn
    initial_castling = board.castling
    initial_en_passant = board.en_passant
    initial_halfmove = board.halfmove
    initial_fullmove = board.fullmove
    
    # Make and unmake several moves
    moves = board.generate_legal_moves()
    for move in moves[:5]:
        board.make_move(move)
        board.unmake_move()
        
        assert board.squares == initial_squares, "Squares should be restored"
        assert board.turn == initial_turn, "Turn should be restored"
        assert board.castling == initial_castling, "Castling should be restored"
        assert board.en_passant == initial_en_passant, "En passant should be restored"
        assert board.halfmove == initial_halfmove, "Halfmove should be restored"
        assert board.fullmove == initial_fullmove, "Fullmove should be restored"

def test_complex_position_make_unmake():
    """Test make/unmake in complex position"""
    board = Board()
    board.setup_starting_position()
    
    # Play several moves
    moves_to_play = [
        Move.encode_move(52, 36),  # e2-e4
        Move.encode_move(12, 28),  # e7-e5
        Move.encode_move(62, 45),  # g1-f3
        Move.encode_move(1, 18),   # b8-c6
    ]
    
    for move in moves_to_play:
        board.make_move(move)
    
    # Save state
    saved_squares = board.squares.copy()
    saved_turn = board.turn
    
    # Make and unmake all legal moves
    legal_moves = board.generate_legal_moves()
    for move in legal_moves:
        board.make_move(move)
        board.unmake_move()
        
        assert board.squares == saved_squares, f"State not restored after {decode_move(move)}"
        assert board.turn == saved_turn, "Turn not restored"


# === Perft-style Test (move generation count) ===
def test_perft_starting_position_depth_2():
    """Count nodes at depth 2 from starting position"""
    board = Board()
    board.setup_starting_position()
    
    def perft(depth):
        if depth == 0:
            return 1
        
        moves = board.generate_legal_moves()
        nodes = 0
        
        for move in moves:
            board.make_move(move)
            nodes += perft(depth - 1)
            board.unmake_move()
        
        return nodes
    
    # Perft(1) = 20, Perft(2) = 400
    assert perft(1) == 20, "Should have 20 moves from starting position"
    assert perft(2) == 400, "Should have 400 nodes at depth 2"


# === Attack Detection Tests ===
def test_knight_attack_detection():
    """Knight attacks are detected correctly"""
    board = Board()
    board.squares = [EMPTY] * 64
    board.squares[27] = W_KNIGHT  # d5
    board.squares[60] = W_KING
    board.white_king_pos = 60
    board.squares[4] = B_KING
    board.black_king_pos = 4
    
    # Knight should attack these squares
    attacked = [10, 12, 17, 21, 33, 37, 42, 44]  # b6, d6, c7, f7, c3, f3, b4, e4
    
    for sq in attacked:
        assert board._is_square_attacked(sq, 1), \
            f"Knight should attack {square_to_coord(sq)}"
    
    # Knight should not attack these squares
    not_attacked = [26, 28, 18, 36]  # adjacent squares
    for sq in not_attacked:
        assert not board._is_square_attacked(sq, 1), \
            f"Knight should not attack {square_to_coord(sq)}"



# --- Helpers ---
def empty_board():
    b = Board()
    b.squares = [EMPTY] * 64
    b.white_king_pos = WHITE_KING_START
    b.black_king_pos = BLACK_KING_START
    b.squares[b.white_king_pos] = W_KING
    b.squares[b.black_king_pos] = B_KING
    b.zobrist_key = b.compute_zobrist()
    return b

# --- Tests for enpassant_available ---
def testenpassant_available_white_pawn():
    b = empty_board()
    # Place white pawn at e5 (square 36), black pawn at d7 (square 11)
    b.squares[28] = W_PAWN
    b.squares[27] = B_PAWN
    b.en_passant = 19  # c6 square index (from_sq+to_sq)//2 for a double pawn push)
    b.turn = 1  # White to move
    assert b.enpassant_available() is True

def testenpassant_not_available_no_adjacent_pawn():
    b = empty_board()
    b.squares[40] = W_PAWN
    b.en_passant = 48
    b.turn = 1
    assert b.enpassant_available() is False

# --- Tests for is_insufficient_material ---
def test_only_kings_draw():
    b = empty_board()
    b.squares[4] = B_KING
    b.squares[60] = W_KING
    assert b.is_insufficient_material() is True

def test_king_and_bishop_vs_king_draw():
    b = empty_board()
    b.squares[4] = B_KING
    b.squares[60] = W_KING
    b.squares[2] = W_BISHOP
    assert b.is_insufficient_material() is True

def test_king_and_two_bishops_not_draw():
    b = empty_board()
    b.squares[4] = B_KING
    b.squares[60] = W_KING
    b.squares[2] = W_BISHOP
    b.squares[5] = W_BISHOP
    assert b.is_insufficient_material() is False

# --- Tests for is_threefold_repetition ---
def test_threefold_repetition_detected():
    b = Board()
    key = b.zobrist_key
    b.repetitions[key] = 3
    assert b.is_threefold_repetition() is True

def test_threefold_repetition_not_detected():
    b = Board()
    key = b.zobrist_key
    b.repetitions[key] = 2
    assert b.is_threefold_repetition() is False

# --- Tests for is_draw ---
def test_draw_by_stalemate(monkeypatch):
    b = empty_board()
    b.squares[4] = B_KING
    b.squares[60] = W_KING
    # Force has_legal_moves to return False, is_in_check to return False
    monkeypatch.setattr(b, "has_legal_moves", lambda: False)
    monkeypatch.setattr(b, "is_in_check", lambda color: False)
    assert b.is_draw() is True

def test_draw_by_fifty_move_rule():
    b = Board()
    b.halfmove = 100
    assert b.is_draw() is True

def test_draw_by_insufficient_material():
    b = empty_board()
    b.squares[4] = B_KING
    b.squares[60] = W_KING
    assert b.is_draw() is True

# --- Tests for hashing ---
def test_zobrist_changes_on_move():
    b = Board()
    b.setup_starting_position()
    initial_key = b.zobrist_key
    move = (12) | (28 << 6)  # black pawn from e7 (12) to e5 (28)
    b.make_move(move)
    assert b.zobrist_key != initial_key

def test_zobrist_restored_on_unmake():
    b = Board()
    b.setup_starting_position()
    initial_key = b.zobrist_key
    move = (12) | (28 << 6)  # black pawn from e7 to e5
    b.make_move(move)
    b.unmake_move()
    assert b.zobrist_key == initial_key

def test_zobristenpassant_file_bit_on_double_push():
    b = Board()
    b.setup_starting_position()

    # Prepare board for the scenario
    b.turn = -1
    b.squares[28] = W_PAWN  # e5, adjacent to EP target
    b.zobrist_key = b.compute_zobrist()   # recompute now that we've mutated the board
    base = b.zobrist_key

    from_sq, to_sq = 11, 27
    move = from_sq | (to_sq << 6)

    # preconditions
    assert b.squares[from_sq] == B_PAWN
    assert b.squares[to_sq] == EMPTY
    assert abs(to_sq - from_sq) == 16

    b.make_move(move)

    assert b.en_passant == (from_sq + to_sq) // 2
    assert b.enpassant_available() is True
    assert b.zobrist_key != base

    b.unmake_move()
    # recompute and compare to the base that included the adjacent pawn
    b.zobrist_key = b.compute_zobrist()
    assert b.zobrist_key == base
