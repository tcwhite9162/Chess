from config import BOARD_SIZE, SQUARE_SIZE, get_starting_position
from game.piece import Piece
import copy

class Board:

    def __init__(self):
        self.king_positions = {'w': None, 'b': None}
        self.rows = self.cols = BOARD_SIZE
        self.turn = "w"
        self.selected = None
        self.needs_rendered = True
        self.en_passant_target = None

        self.grid = self.generate_starting_grid()

    def generate_starting_grid(self):
        board = get_starting_position() # have to use function as copy can't pickle pygame surface (?)
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                piece = board[r][c]
                if piece and piece.type == 'k':
                    self.king_positions[piece.color] = (r, c)
        return board
    
    def reset_board(self):
        self.king_positions = {'w': None, 'b': None}
        self.grid = get_starting_position()
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                piece = self.grid[r][c]
                if piece and piece.type == 'k':
                    self.king_positions[piece.color] = (r, c)
        self.turn = "w"
        self.selected = None
        self.needs_rendered = True
        self.en_passant_target = None
        
    
    def piece_at(self, row, col):
        return self.grid[row][col]
    
    def apply_move(self, starting_pos, target_pos):
        piece = self.piece_at(*starting_pos)

        if piece.type == 'p' and target_pos == self.en_passant_target:
            captured_row = starting_pos[0]
            captured_col = target_pos[1]
            self.grid[captured_row][captured_col] = None

        if piece.type == 'p' and abs(starting_pos[0] - target_pos[0]) == 2:
            row = (starting_pos[0] + target_pos[0]) // 2
            self.en_passant_target = (row, starting_pos[1])
        else:
            self.en_passant_target = None

        if piece.type == 'k' and abs(starting_pos[1] - target_pos[1]) == 2: # only happens when castling
            row = starting_pos[0]
            if target_pos[1] > starting_pos[1]: # King side
                self.grid[row][5] = self.grid[row][7]
                self.grid[row][7] = None
            else:                               # Queen side
                self.grid[row][3] = self.grid[row][0]
                self.grid[row][0] = None

        self.grid[target_pos[0]][target_pos[1]]     = piece
        self.grid[starting_pos[0]][starting_pos[1]] = None

        if piece.type == 'k':
            self.king_positions[piece.color] = target_pos

        if piece.type == 'p':
            promotion_rank = 0 if piece.color == 'w' else 7
            if target_pos[0] == promotion_rank:
                self.promote_pawn(target_pos[0], target_pos[1], piece.color)

        self.turn = "b" if self.turn == "w" else "w"


    def flag_for_redraw(self):
        self.needs_rendered = True

    def pseudo_legal_moves(self, row, col):
        piece = self.grid[row][col]
        if piece is None:
            return [], []
        
        moves    = []
        captures = []
        if piece.type == "p":
            moves, captures = self.pawn_moves(  row, col, piece.color)
        if piece.type == "n":
            moves, captures = self.knight_moves(row, col, piece.color)
        if piece.type == "b":
            moves, captures = self.bishop_moves(row, col, piece.color)
        if piece.type == "r":
            moves, captures = self.rook_moves(  row, col, piece.color)
        if piece.type == "q":
            moves, captures = self.queen_moves( row, col, piece.color)
        if piece.type == "k":
            moves, captures = self.king_moves(  row, col, piece.color)

        return moves, captures
    
    def legal_moves(self, row, col):
        piece = self.grid[row][col]
        if not piece or piece.color != self.turn:
            return [], []
        
        moves, captures = self.pseudo_legal_moves(row, col)
        legal_moves = []
        legal_captures = []

        for target in moves + captures:
            # store starting position
            captured = self.grid[target[0]][target[1]]
            initial_king_pos = self.king_positions[piece.color]
            initial_piece = self.grid[row][col]

            # make move on board
            self.grid[target[0]][target[1]] = piece
            self.grid[row][col] = None

            if piece.type == 'k':
                self.king_positions[piece.color] = target
            # check if move results in check
            in_check = self.is_in_check(piece.color)

            # undo move
            self.grid[row][col] = initial_piece
            self.grid[target[0]][target[1]] = captured
            self.king_positions[piece.color] = initial_king_pos


            if not in_check:
                if target in moves:
                    legal_moves.append(target)
                else:
                    legal_captures.append(target)
            
        return legal_moves, legal_captures
    
    def pawn_moves(self, row, col, color):
        direction = -1 if color == 'w' else 1 
        start_row = 6  if color == 'w' else 1 # 2nd and 7nk rank (0 indexed)
        moves    = []
        captures = []

        # Move forward
        if 0 <= row + direction < 8 and self.grid[row + direction][col] is None:
            moves.append((row + direction, col))
            if row == start_row and 0 <= row + direction < 8 and self.grid[row + direction * 2][col] is None:
                moves.append((row + direction * 2, col))

        # Diagonal captures
        for dcol in [-1, 1]:
            new_col = col + dcol
            new_row = row + direction

            if 0 <= new_row < 8 and 0 <= new_col < 8:
                target = self.grid[new_row][new_col]
                if target and target.color != color:
                    captures.append((new_row, new_col))

        if self.en_passant_target:
            for dc in [-1, 1]:
                ep_row = row + direction
                ep_col = col + dc
                if (ep_row, ep_col) == self.en_passant_target:
                    target = self.grid[row][ep_col]
                    if target and target.type == 'p' and target.color != color:
                        captures.append((ep_row, ep_col))

        return moves, captures

    def knight_moves(self, row, col, color):
        offsets = ((-2, 1), (-2, -1), (2,  1), (2,  -1),
                   (1,  2), (1,  -2), (-1, 2), (-1, -2))

        moves = []
        captures = []
        for dr, dc in offsets:
            new_row = row + dr
            new_col = col + dc

            if 0 <= new_row < 8 and 0 <= new_col < 8:
                target = self.grid[new_row][new_col]
                if target is None:
                    moves.append((new_row, new_col))
                elif target.color != color:
                    captures.append((new_row, new_col))
        return moves, captures
    
    def king_moves(self, row, col, color):
        moves = []
        captures = []

        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                new_row = row + dr
                new_col = col + dc

                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    target = self.grid[new_row][new_col]
                    
                    if target is None:
                        moves.append((new_row, new_col))
                    elif target.color != color:
                        captures.append((new_row, new_col))

        if self.can_castle_kingside(color):
            moves.append((row, col + 2))
        if self.can_castle_queenside(color):
            moves.append((row, col - 2))
        return moves, captures

    def bishop_moves(self, row, col, color):
        directions = ((1, 1), (1, -1), (-1, 1), (-1, -1))
        return self.get_sliding_moves(row, col, color, directions)

    def rook_moves(self, row, col, color):
        directions = ((1, 0), (-1, 0), (0, 1), (0, -1))
        return self.get_sliding_moves(row, col, color, directions)

    def queen_moves(self, row, col, color):
        directions = ((1, 1), (1, -1), (-1, 1), (-1, -1), 
                      (1, 0), (-1, 0), (0,  1), (0,  -1))
        return self.get_sliding_moves(row, col, color, directions)

    def get_sliding_moves(self, row, col, color, directions):
        moves = []
        captures = []

        for dr, dc in directions:
            new_row = row + dr
            new_col = col + dc

            while 0 <= new_row < 8 and 0 <= new_col < 8:
                target = self.grid[new_row][new_col]

                if target is None:
                    moves.append((new_row, new_col))
                elif target.color != color:
                    captures.append((new_row, new_col))
                    break
                else:
                    break

                new_row += dr
                new_col += dc
        return moves, captures

    def can_castle_kingside(self, color):
        row = 7 if color == 'w' else 0
        return (
            self.grid[row][5] is None and 
            self.grid[row][6] is None and
            isinstance(self.grid[row][7], Piece) and
            self.grid[row][7].type == 'r' and 
            self.grid[row][7].color == color
        )

    def can_castle_queenside(self, color):
        row = 7 if color == 'w' else 0
        return (
            self.grid[row][1] is None and 
            self.grid[row][2] is None and
            self.grid[row][3] is None and
            isinstance(self.grid[row][0], Piece) and
            self.grid[row][0].type == 'r' and 
            self.grid[row][0].color == color
        )

    def squares_attacked_by_piece(self, row, col):
        piece = self.grid[row][col]
        if piece is None:
            return []

        attacked = []
        if piece.type == 'p':
            direction = -1 if piece.color == 'w' else 1
            for dc in [-1, 1]:
                if 0 <= row + direction < 8 and 0 <= col + dc < 8:
                    attacked.append((row + direction, col + dc))

        elif piece.type == 'n':
            directions = [(-2, 1),(-2, -1),(2, 1),(2, -1),
                          (1, 2),(1, -2),(-1, 2),(-1, -2)]

            for dr, dc in directions:
                r, c = row + dr, col + dc
                if 0 <= r < 8 and 0 <= c < 8:
                    attacked.append((r, c))

        elif piece.type in ['r', 'q', 'b']:
            directions = []
            if piece.type in ['b', 'q']:
                directions += [(1, 1), (1, -1), (-1, 1), (-1, -1)]
            if piece.type in ['r', 'q']:
                directions += [(0, 1), (0, -1), (1, 0), (-1, 0)]

            for dr, dc in directions:
                r, c = row + dr, col + dc
                while 0 <= r < 8 and 0 <= c < 8:
                    attacked.append((r, c))
                    if self.grid[r][c] is not None:
                        break
                    r += dr
                    c += dc

        elif piece.type == 'k':
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    r, c = row + dr, col + dc
                    if 0 <= r < 8 and 0 <= c < 8:
                        attacked.append((r, c))
        return attacked
    
    def squares_attacked_by_color(self, color):
        attacked = set()
        for r in range(self.rows):
            for c in range(self.cols):
                piece = self.grid[r][c]
                if piece and piece.color == color:
                    attacked.update(self.squares_attacked_by_piece(r, c))
        return attacked
    
    def is_in_check(self, color):
        king_pos = self.king_positions[color]
        enemy_color = 'b' if color == 'w' else 'w'

        return king_pos in self.squares_attacked_by_color(enemy_color)
    
    def check_pos(self, color):
        # used by renderer
        return self.king_positions[color] if self.is_in_check(color) else None
    
    def promote_pawn(self, row, col, color, new_type='q'):
        self.grid[row][col] = Piece(color, new_type, SQUARE_SIZE)

    def __repr__(self):
        rows = []
        
        # Column labels
        col_labels = "    " + "   ".join(chr(97 + col) for col in range(8))  # a - h
        rows.append(col_labels)
        rows.append("  ┌" + "───┬" * 7 + "───┐")  # top line

        for i, row in enumerate(self.grid):
            row_repr = []
            for piece in row:
                if piece is None:
                    row_repr.append(" . ")
                else:
                    row_repr.append(f"{piece.code:>3}")
            rows.append(f"{8 - i} │" + "│".join(row_repr) + "│")

            if i < 7:
                rows.append("  ├" + "───┼" * 7 + "───┤")  # middle lines
            else:
                rows.append("  └" + "───┴" * 7 + "───┘")  # bottom line

        return "\n".join(rows)