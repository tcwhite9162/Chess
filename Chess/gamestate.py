from config import COLOR_PALETTES, BOARD_ORIGIN_X, BOARD_ORIGIN_Y, SQUARE_SIZE, HIGHLIGHT_COLORS
from game.board import Board

class GameState:
    def __init__(self, active_palette_index=0, contrast_level=0):
        self.available_palettes = list(COLOR_PALETTES.keys())
        self.active_palette_index = active_palette_index
        self.contrast_level = contrast_level # 0 = low, 1 = high
        self.palette_count = len(self.available_palettes)
        self.selected_square = None # (rank, file)
        self.turn = 'w'
        self.available_moves = []
        self.available_captures = []
        self.awaiting_promotion = None # (rank, file, color)
        self.castling_rights = {'w': {'k': True, 'q': True}, 
                                'b': {'k': True, 'q': True}}
        self.halfmove_clock  = 0
        self.fullmove_number = 1
        self.is_checkmate    = False
        self.is_stalemate    = False
        self.is_gameover     = False
        self.winner          = None
        

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
            board.update_castling_rights(self.castling_rights)

            if end in self.available_moves or end in self.available_captures:
                moving_piece = board.piece_at(*start)
                self.update_castling_rights(start, moving_piece)
                promotion_needed = board.apply_move(start, end)
                if promotion_needed:
                    self.awaiting_promotion = (end[0], end[1], moving_piece.color)
                    board.flag_for_redraw()
                    return

                board.flag_for_redraw()
                self.toggle_turn()

                self.update_move_counters(moving_piece, board.piece_at(*end))
                self.check_gameover(board)
            
            self.clear_selection()

        elif clicked_piece and clicked_piece.color == self.turn:
            self.selected_square = (row, col)
            self.available_moves, self.available_captures = board.legal_moves(row, col, self.turn)

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
        if piece is None:
            return
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
        color = self.turn
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
    
    def check_gameover(self, board):
        if board.is_in_check(self.turn):
            if not board.has_legal_moves(self.turn):
                self.is_checkmate = self.is_gameover = True
                self.winner = 'White' if self.turn == 'b' else 'Black'
        else:
            if not board.has_legal_moves(self.turn):
                self.is_stalemate = self.is_gameover = True


    def update_move_counters(self, moving_piece, captured_piece):
        if moving_piece.type == 'p' or captured_piece:
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1

        if self.turn == 'b':
            self.fullmove_number += 1

    def toggle_turn(self):
        self.turn = 'b' if self.turn == 'w' else 'w'

    