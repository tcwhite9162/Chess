from config import STARTING_POSITION, BOARD_SIZE

class Board:

    def __init__(self, default_position=1):
        self.grid = self.create_initial_position(default_position)
        self.turn = "w"
        self.selected = None
        self.needs_rendered = True
        self.rows = self.cols = BOARD_SIZE

    def create_initial_position(self, default):
        board = STARTING_POSITION if default else [[None for _ in range(8)] for _ in range(8)]
        return board
    
    def get_piece(self, row, col):
        return self.grid[row][col]
    
    def move_piece(self, starting_pos, target_pos):
        piece = self.get_piece(*starting_pos)

        self.grid[target_pos[0]][target_pos[1]]     = piece
        self.grid[starting_pos[0]][starting_pos[1]] = None

        self.turn = "b" if self.turn == "w" else "w"

    def mark_dirty(self):
        self.needs_rendered = True

    def get_legal_moves(self, row, col):
        piece = self.grid[row][col]
        if piece is None:
            return
        
        moves = []
        if piece.type == "p":
            moves = self.get_pawn_moves(  row, col, piece.color)
        if piece.type == "n":
            moves = self.get_knight_moves(row, col, piece.color)
        if piece.type == "b":
            moves = self.get_bishop_moves(row, col, piece.color)
        if piece.type == "r":
            moves = self.get_rook_moves(  row, col, piece.color)
        if piece.type == "q":
            moves = self.get_queen_moves( row, col, piece.color)
        if piece.type == "k":
            moves = self.get_king_moves(  row, col, piece.color)

        return moves
    
    def get_pawn_moves(self, row, col, color):
        direction = -1 if color == 'w' else 1
        start_row = 6 if color == 'w' else 1
        moves = []

        # Move forward
        if self.grid[row + direction][col] is None:
            moves.append((row + direction, col))
            if row == start_row and self.grid[row + direction * 2][col] is None:
                moves.append((row + direction * 2, col))

        # Diagonal captures
        for dcol in [-1, 1]:
            new_col = col + dcol
            new_row = row + direction

            if 0 <= new_row < 8 and 0 <= new_col < 8:
                target = self.grid[new_row][new_col]
                if target and target.color != color:
                    moves.append((new_row, new_col))
        return moves

    def get_knight_moves(self, row, col, color):
        offsets = ((-2, 1), (-2, -1), (2,  1), (2,  -1),
                   (1,  2), (1,  -2), (-1, 2), (-1, -2))

        moves = []
        for dr, dc in offsets:
            new_row = row + dr
            new_col = col + dc

            if 0 <= new_row < 8 and 0 <= new_col < 8:
                target = self.grid[new_row][new_col]
                if target is None or target.color != color:
                    moves.append((new_row, new_col))
        return moves

    def get_bishop_moves(self, row, col, color):
        directions = ((1, 1), (1, -1), (-1, 1), (-1, -1))
        return self.get_sliding_moves(row, col, color, directions)

    def get_rook_moves(self, row, col, color):
        directions = ((1, 0), (-1, 0), (0, 1), (0, -1))
        return self.get_sliding_moves(row, col, color, directions)

    def get_queen_moves(self, row, col, color):
        directions = ((1, 1), (1, -1), (-1, 1), (-1, -1), 
                      (1, 0), (-1, 0), (0,  1), (0,  -1))
        return self.get_sliding_moves(row, col, color, directions)

    def get_king_moves(self, row, col, color):
        moves = []

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
                        moves.append((new_row, new_col))
                        break
        return moves

    def get_sliding_moves(self, row, col, color, directions):
        moves = []

        for dr, dc in directions:
            new_row = row + dr
            new_col = col + dc

            while 0 <= new_row < 8 and 0 <= new_col < 8:
                target = self.grid[new_row][new_col]

                if target is None:
                    moves.append((new_row, new_col))
                elif target.color != color:
                    moves.append((new_row, new_col))
                    break
                else:
                    break

                new_row += dr
                new_col += dc
        return moves

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