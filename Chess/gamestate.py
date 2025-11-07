from config import COLOR_PALETTES, BOARD_ORIGIN_X, BOARD_ORIGIN_Y, SQUARE_SIZE, HIGHLIGHT_COLORS

class GameState:
    def __init__(self, palette_index=0, contrast_index=0):
        self.palette_names   = list(COLOR_PALETTES.keys())
        self.palette_index   = palette_index
        self.contrast_index  = contrast_index # 0 = low, 1 = high
        self.num_palettes    = len(self.palette_names)
        self.selected_square = None
        self.legal_moves     = []

    def current_colors(self):
        palette_name = self.palette_names[self.palette_index]
        palette = COLOR_PALETTES[palette_name]
        colors = list(palette.values())[self.contrast_index]
        return (*colors, HIGHLIGHT_COLORS[self.palette_index])
    
    def increase_palette_index(self):
        self.palette_index = (self.palette_index + 1) % self.num_palettes

    def decrease_palette_index(self):
        self.palette_index = (self.palette_index - 1) % self.num_palettes

    def toggle_contrast(self):
        self.contrast_index = 0 if self.contrast_index else 1

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

            if end in self.legal_moves:
                board.move_piece(start, end)
                board.mark_dirty()
            
            self.selected_square = None
            self.legal_moves = []

        elif clicked_piece and clicked_piece.color == board.turn:
            self.selected_square = (row, col)
            self.legal_moves = board.get_legal_moves(row, col)
        
        else:
            self.selected_square = None
            self.legal_moves = []

        
        board.mark_dirty()