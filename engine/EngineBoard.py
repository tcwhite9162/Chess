import constants as C
from move import Move
import MoveGen

class Board:
    def __init__(self):
        self.squares = [0] * 64

        self.turn = 1           # -1 for black
        self.castling = 0b1111  # as KQkq 
        self.en_passant = -1
        self.halfmove = 0
        self.fullmove = 1

        self.white_king_pos = C.WHITE_KING_START
        self.black_king_pos = C.BLACK_KING_START

        self.history = []

    def generate_legal_moves(self):
        legal_moves = []
        
        for move in self.generate_pseudo_legal_moves():
            self.make_move(move)
            if not self.is_in_check(-self.turn):
                legal_moves.append(move)
            self.unmake_move()
        
        return legal_moves

    def generate_pseudo_legal_moves(self):
        moves = []

        for square in range(64):
            piece = self.squares[square]
            if piece * self.turn <= 0:
                continue # not our piece
            
            piece_type = abs(piece)
            if piece_type == 1: # pawn
                moves.extend(MoveGen.generate_pawn_moves(self, square))
            elif piece_type == 2: # knight
                moves.extend(MoveGen.generate_knight_moves(self, square))
            elif piece_type == 3: # bishop
                moves.extend(MoveGen.generate_bishop_moves(self, square))
            elif piece_type == 4: # rook
                moves.extend(MoveGen.generate_rook_moves(self, square))
            elif piece_type == 5: # queen
                moves.extend(MoveGen.generate_queen_moves(self, square))
            elif piece_type == 6: # king
                moves.extend(MoveGen.generate_king_moves(self, square))

        return moves

    def make_move(self, move):
        from_sq =  move & 0x3F
        to_sq   = (move >> 6) & 0x3F
        flags   = (move >> 12) & 0xF

        self.history.append({
            'move': move,
            'captured': self.squares[to_sq],
            'castling': self.castling,
            'en_passant': self.en_passant,
            'halfmove': self.halfmove,
            'flags': flags
        })

        piece = self.squares[from_sq]
        self.squares[from_sq] = C.EMPTY
        # en passant
        if flags == C.EN_PASSANT:
            if self.turn == 1:
                captured_sq = to_sq + C.DOWN
            else:
                captured_sq = to_sq + C.UP

            self.history[-1]['captured'] = self.squares[captured_sq]
            self.squares[captured_sq] = C.EMPTY
            self.squares[to_sq] = piece

        # promotion
        if flags in (C.PROMOTION_QUEEN, C.PROMOTION_QUEEN_CAPTURE):
            self.squares[to_sq] = C.W_QUEEN if self.turn == 1 else C.B_QUEEN
            
        elif flags in (C.PROMOTION_ROOK, C.PROMOTION_ROOK_CAPTURE):
            self.squares[to_sq] = C.W_ROOK if self.turn == 1 else C.B_ROOK
            
        elif flags in (C.PROMOTION_BISHOP, C.PROMOTION_BISHOP_CAPTURE):
            self.squares[to_sq] = C.W_BISHOP if self.turn == 1 else C.B_BISHOP
            
        elif flags in (C.PROMOTION_KNIGHT, C.PROMOTION_KNIGHT_CAPTURE):
            self.squares[to_sq] = C.W_KNIGHT if self.turn == 1 else C.B_KNIGHT
        else:
            self.squares[to_sq] = piece

        # en passant target update
        self.en_passant = -1
        if abs(piece) == 1 and abs(to_sq - from_sq) == 16: # pawn moved 2 squares
            self.en_passant = (from_sq + to_sq) // 2

        if flags == C.CASTLING:
            if piece == C.W_KING:
                if to_sq == C.WHITE_KINGSIDE_CASTLE: # white castling kingside
                    self.squares[C.WHITE_ROOK_H1] = C.EMPTY
                    self.squares[C.WHITE_ROOK_F1] = C.W_ROOK
                elif to_sq == C.WHITE_QUEENSIDE_CASTLE: # white castling queenside
                    self.squares[C.WHITE_ROOK_A1] = C.EMPTY
                    self.squares[C.WHITE_ROOK_D1] = C.W_ROOK
            
                self.white_king_pos = to_sq
                self.castling &= 0b1100 # clear white castling rights
            
            elif piece == C.B_KING:
                if to_sq == C.BLACK_KINGSIDE_CASTLE: # black castling kingside
                    self.squares[C.BLACK_ROOK_H8] = C.EMPTY
                    self.squares[C.BLACK_ROOK_F8] = C.B_ROOK
                elif to_sq == C.BLACK_QUEENSIDE_CASTLE: # black castling queenside
                    self.squares[C.BLACK_ROOK_A8] = C.EMPTY
                    self.squares[C.BLACK_ROOK_D8] = C.B_ROOK
                
                self.black_king_pos = to_sq
                self.castling &= 0b0011
        
        # halfmove clock update
        if abs(piece) == 1 or flags & C.CAPTURE:
            self.halfmove = 0
        else:
            self.halfmove += 1

        # update castling rights
        self._update_castling_rights(from_sq, to_sq, piece, self.history[-1]['captured'])

        # flip turn
        self.turn *= -1
        if self.turn == 1:
            self.fullmove += 1
        
    def unmake_move(self):
        # undo most recent move
        state = self.history.pop()
        move = state['move']

        from_sq = move & 0x3F
        to_sq   = (move >> 6) & 0x3F
        flags   = state['flags']

        # default
        piece = self.squares[to_sq]

        # undo promotion
        if flags in (C.PROMOTION_QUEEN, C.PROMOTION_QUEEN_CAPTURE, C.PROMOTION_ROOK, 
                     C.PROMOTION_ROOK_CAPTURE, C.PROMOTION_BISHOP, C.PROMOTION_BISHOP_CAPTURE, 
                     C.PROMOTION_KNIGHT, C.PROMOTION_KNIGHT_CAPTURE):

            pawn = C.W_PAWN if self.turn == -1 else C.B_PAWN
            self.squares[from_sq] = pawn
            
        else:
            self.squares[from_sq] = piece

        if flags == C.CASTLING:
            self.squares[from_sq] = C.W_KING if self.turn == -1 else C.B_KING
            if to_sq == C.WHITE_KINGSIDE_CASTLE:  # white king-side
                self.squares[C.WHITE_ROOK_H1] = C.W_ROOK
                self.squares[C.WHITE_ROOK_F1] = C.EMPTY

            elif to_sq == C.WHITE_QUEENSIDE_CASTLE:  # white queen-side
                self.squares[C.WHITE_ROOK_A1] = C.W_ROOK
                self.squares[C.WHITE_ROOK_D1] = C.EMPTY

            elif to_sq == C.BLACK_KINGSIDE_CASTLE:   # black king-side
                self.squares[C.BLACK_ROOK_H8] = C.B_ROOK
                self.squares[C.BLACK_ROOK_F8] = C.EMPTY

            elif to_sq == C.BLACK_QUEENSIDE_CASTLE:   # black queen-side
                self.squares[C.BLACK_ROOK_A8] = C.B_ROOK
                self.squares[C.BLACK_ROOK_D8] = C.EMPTY

        # undo en passant capture
        if flags == C.EN_PASSANT:
            self.squares[from_sq] = C.W_PAWN if self.turn == -1 else C.B_PAWN
            if self.turn == -1: # white move was just undone
                captured_sq = to_sq + C.DOWN
                self.squares[captured_sq] = C.B_PAWN
            else:               # black move was just undone
                captured_sq = to_sq + C.UP
                self.squares[captured_sq] = C.W_PAWN

        # replace captured piece (or empty square)
        self.squares[to_sq] = state['captured']

        # restore game state
        self.castling = state['castling']
        self.en_passant = state['en_passant']
        self.halfmove = state['halfmove']

        # restore king positions
        if piece == C.W_KING or flags == C.CASTLING:
            self.white_king_pos = from_sq
        elif piece == C.B_KING or flags == C.CASTLING:
            self.black_king_pos = from_sq
        
        # flip turn 
        self.turn *= -1
        if self.turn == -1:
            self.fullmove -= 1

   
    def is_in_check(self, color):
        king_pos = self.white_king_pos if color == 1 else self.black_king_pos
        return self._is_square_attacked(king_pos, -color)
    

    def piece_at(self, square):
        return self.squares[square]

    def is_valid_square(self, square):
        return 0 <= square < 64
    
    def has_legal_moves(self):
        return len(self.generate_legal_moves()) > 0
    
    def is_checkmate(self):
        return self.is_in_check(self.turn) and not self.has_legal_moves()
    
    def is_stalemate(self):
        return not self.is_in_check(self.turn) and not self.has_legal_moves()

    def setup_starting_position(self):
        # standard starting position
        self.squares[0] = self.squares[7] = C.B_ROOK
        self.squares[1] = self.squares[6] = C.B_KNIGHT
        self.squares[2] = self.squares[5] = C.B_BISHOP
        self.squares[3] = C.B_QUEEN
        self.squares[4] = C.B_KING
        
        self.squares[56] = self.squares[63] = C.W_ROOK
        self.squares[57] = self.squares[62] = C.W_KNIGHT
        self.squares[58] = self.squares[61] = C.W_BISHOP
        self.squares[60] = C.W_KING
        self.squares[59] = C.W_QUEEN

        for i in C.BLACK_PAWN_ROW:
            self.squares[i] = C.B_PAWN

        for j in C.WHITE_PAWN_ROW:
            self.squares[j] = C.W_PAWN

    def _update_castling_rights(self, from_sq, to_sq, piece, captured):
        # clear castling if king moves
        if piece == C.W_KING:
            self.castling &= 0b1100
            self.white_king_pos = to_sq
        elif piece == C.B_KING:
            self.castling &= 0b0011
            self.black_king_pos = to_sq

        # if rook moves
        if from_sq == C.WHITE_ROOK_H1:               # white rook h1
            self.castling &= 0b1110
        elif from_sq == C.WHITE_ROOK_A1:             # white rook a1
            self.castling &= 0b1101
        elif from_sq == C.BLACK_ROOK_H8:              # black rook h8
            self.castling &= 0b1011
        elif from_sq == C.BLACK_ROOK_A8:              # black rook a8
            self.castling &= 0b0111

        # if rook captured
        if captured == C.W_ROOK:
            if to_sq == C.WHITE_ROOK_H1: self.castling &= 0b1110
            if to_sq == C.WHITE_ROOK_A1: self.castling &= 0b1101
        elif captured == C.B_ROOK:
            if to_sq == C.BLACK_ROOK_H8: self.castling &= 0b1011
            if to_sq == C.BLACK_ROOK_A8: self.castling &= 0b0111

    def _is_square_attacked(self, square, attacking_color):
        sq_rank = square // 8
        sq_file = square % 8

        pawn_file = (square % 8)  # file of the square being attacked

        # Pawns
        if attacking_color == 1:  # white pawns
            for offset in (C.DOWN_LEFT, C.DOWN_RIGHT):
                target = square + offset
                if self.is_valid_square(target):
                    tr, tf = target // 8, target % 8
                    # ensure diagonal: file difference must be 1
                    if abs(tf - (square % 8)) == 1 and self.squares[target] == C.W_PAWN:
                        return True
        else:  # black pawns
            for offset in (C.UP_LEFT, C.UP_RIGHT):
                target = square + offset
                if self.is_valid_square(target):
                    tr, tf = target // 8, target % 8
                    if abs(tf - (square % 8)) == 1 and self.squares[target] == C.B_PAWN:
                        return True

        
        # Knights
        for offset in C.KNIGHT_DIRS:
            target = square + offset
            if not self.is_valid_square(target):
                continue
            tr, tf = target // 8, target % 8
            if abs(tr - sq_rank) <= 2 and abs(tf - sq_file) <= 2:
                piece = self.squares[target]
                if attacking_color == 1 and piece == C.W_KNIGHT:
                    return True
                if attacking_color == -1 and piece == C.B_KNIGHT:
                    return True

        # Bishops / Queens (diagonals)
        for direction in C.BISHOP_DIRS:
            current = square + direction
            while self.is_valid_square(current):
                # prevent wrap: ensure we didn’t jump across the board horizontally
                if abs((current % 8) - ((current - direction) % 8)) != 1:
                    break

                piece = self.squares[current]
                if piece != C.EMPTY:
                    if attacking_color == 1 and piece in (C.W_BISHOP, C.W_QUEEN):
                        return True
                    if attacking_color == -1 and piece in (C.B_BISHOP, C.B_QUEEN):
                        return True
                    break
                current += direction

        # Rooks / Queens (orthogonals)
        for direction in C.ROOK_DIRS:
            current = square + direction
            while self.is_valid_square(current):
                cf = current % 8
                # if moving left, stop if we wrapped from file 0 to 7
                if direction == C.LEFT and cf == 7:
                    break
                # if moving right, stop if we wrapped from file 7 to 0
                if direction == C.RIGHT and cf == 0:
                    break

                piece = self.squares[current]
                if piece != C.EMPTY:
                    if attacking_color == 1 and piece in (C.W_ROOK, C.W_QUEEN):
                        return True
                    if attacking_color == -1 and piece in (C.B_ROOK, C.B_QUEEN):
                        return True
                    break
                current += direction


        # Kings
        for direction in C.KING_DIRS:
            target = square + direction
            if not self.is_valid_square(target):
                continue
            tr, tf = target // 8, target % 8
            if abs(tr - sq_rank) <= 1 and abs(tf - sq_file) <= 1:
                piece = self.squares[target]
                if attacking_color == 1 and piece == C.W_KING:
                    return True
                if attacking_color == -1 and piece == C.B_KING:
                    return True

        return False