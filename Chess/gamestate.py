from config import COLOR_PALETTES, BOARD_ORIGIN_X, BOARD_ORIGIN_Y, SQUARE_SIZE, HIGHLIGHT_COLORS

class GameState:
    def __init__(self, active_palette_index=0, contrast_level=0):
        self.available_palettes   = list(COLOR_PALETTES.keys())
        self.active_palette_index   = active_palette_index
        self.contrast_level  = contrast_level # 0 = low, 1 = high
        self.palette_count    = len(self.available_palettes)
        self.selected_square = None
        self.available_moves     = []
        self.available_captures        = []
        self.castling_rights = {'w': {'k': True, 'q': True}, 
                                'b': {'k': True, 'q': True}}
        

    def active_colors(self):
        palette_name = self.available_palettes[self.active_palette_index]
        palette = COLOR_PALETTES[palette_name]
        colors = list(palette.values())[self.contrast_level]
        return (*colors, HIGHLIGHT_COLORS[self.active_palette_index])
    
    def next_palette(self):
        self.active_palette_index = (self.active_palette_index + 1) % self.palette_count

    def previous_palette(self):
        self.active_palette_index = (self.active_palette_index - 1) % self.palette_count

    def toggle_contrast_level(self):
        self.contrast_level = 0 if self.contrast_level else 1

    def handle_click(self, position, board):
        x, y = position
        col = (x - BOARD_ORIGIN_X) // SQUARE_SIZE
        row = (y - BOARD_ORIGIN_Y) // SQUARE_SIZE

        if not (0 <= row < 8 and 0 <= col < 8):
            return # Clicked outside board

        clicked_piece = board.grid[row][col]

        if self.selected_square:
            start = self.selected_square
            end = (row, col)

            if end in self.available_moves or end in self.available_captures:
                moving_piece = board.piece_at(*start)
                self.update_castling_rights(start, moving_piece)
                board.apply_move(start, end)
                board.flag_for_redraw()
            
            self.clear_selection()

        elif clicked_piece and clicked_piece.color == board.turn:
            self.selected_square = (row, col)
            self.available_moves, self.available_captures = board.legal_moves(row, col)

            if clicked_piece.type == 'k':
                self.available_moves = self.validate_castling_moves(board, row, col, self.available_moves)
            
        else:
            self.clear_selection()
        

        board.flag_for_redraw()

    def clear_selection(self):
        self.selected_square = None
        self.available_moves = []
        self.available_captures = []


    def update_castling_rights(self, start, piece):
        color = piece.color

        if piece.type == 'k':
            self.castling_rights[color]['k'] = False
            self.castling_rights[color]['q'] = False
        
        if piece.type == 'r':
            if color == 'w':
                if start == (7, 0):
                    self.castling_rights['w']['q'] = False
                elif start == (7, 7):
                    self.castling_rights['w']['k'] = False
            elif color == 'b':
                if start == (0, 0):
                    self.castling_rights['b']['q'] = False
                elif start == (0, 7):
                    self.castling_rights['b']['k'] = False
    
    def validate_castling_moves(self, board, row, col, moves):
        color = board.turn
        filtered_moves = []

        for move in moves:
            if move == (row, col + 2):
                if not self.castling_rights[color]['k']:
                    continue
                if any(self.is_square_attacked(board, row, col + offset, color) for offset in [0, 1, 2]):
                    continue

            if move == (row, col - 2):
                if not self.castling_rights[color]['q']:
                    continue
                if any(self.is_square_attacked(board, row, col - offset, color) for offset in [0, 1, 2]):
                    continue

            filtered_moves.append(move)

        return filtered_moves

    def is_square_attacked(self, board, row, col, defending_color):
        for r in range(board.rows):
            for c in range(board.cols):
                piece = board.grid[r][c]
                if piece and piece.color != defending_color:
                    attacked = board.squares_attacked_by_piece(r, c)
                    if (row, col) in attacked:
                        return True
        return False