from helpers.hash_position import encode_position
from helpers.clock import ClockManager
from helpers.theme import ThemeManager
from game.history import GameHistory
import config as cfg

class GameState:
    def __init__(self, active_palette_index=0, contrast_level=0, initial_time=600, increment=0):
        self.theme   = ThemeManager(active_palette_index, contrast_level)
        self.clock   = ClockManager(initial_time, increment)
        self.history = GameHistory()
        self.turn            = 'w'
        self.selected_square = None  # (rank, file)
        self.available_moves = []
        self.available_captures = []
        self.awaiting_promotion = None # (rank, file, color)
        self.castling_rights    = {'w': {'k': True, 'q': True},
                                   'b': {'k': True, 'q': True}}
        self.position_counts = {}
        self.halfmove_clock  = 0
        self.fullmove_number = 1
        self.status = {
            'is_checkmate': False,
            'is_stalemate': False,
            'is_draw': False,
            'is_gameover': False,
            'winner': None,
            'reason': None
        }

    def handle_click(self, position, board):
        print(self.fullmove_number, self.halfmove_clock)
        if not self.clock.clock_started and self.turn == 'w': # start clock on first click
            self.clock.unpause()
            self.clock.clock_started = True

        x, y = position
        col = (x - cfg.BOARD_ORIGIN_X) // cfg.SQUARE_SIZE
        row = (y - cfg.BOARD_ORIGIN_Y) // cfg.SQUARE_SIZE

        if not (0 <= row < 8 and 0 <= col < 8):
            return # Clicked outside board

        clicked_piece = board.grid[row][col]

        if self.selected_square:
            start = self.selected_square
            end = (row, col)
            board.update_castling_rights(self.castling_rights)


            if end in self.available_moves or end in self.available_captures:
                moving_piece = board.piece_at(*start)
                captured_piece = board.piece_at(*end)

                self.update_castling_rights(start, moving_piece)
                
                if captured_piece and captured_piece.type == 'r':
                    self.update_castling_rights(end, captured_piece)

                promotion_needed = board.apply_move(start, end)

                if promotion_needed:
                    self.awaiting_promotion = (end[0], end[1], moving_piece.color, captured_piece)
                    board.flag_for_redraw()

                    return

                self.update_move_counters(moving_piece, captured_piece)
                board.flag_for_redraw()
                self.toggle_turn()

                key = encode_position(board.grid, self.turn, self.castling_rights, board.en_passant_target)
                self.position_counts[key] = self.position_counts.get(key, 0) + 1

                self.save_position(board)
                self.clock.switch_turn()

                if self.check_draw(key):
                    self.status['is_draw']     = True
                    self.status['is_gameover'] = True
                else:
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

    def complete_promotion(self, board, piece_type):
        if not self.awaiting_promotion:
            return

        row, col, color, captured_piece = self.awaiting_promotion
        board.promote_pawn(row, col, color, piece_type)

        moving_piece = board.piece_at(row, col)

        self.update_move_counters(moving_piece, captured_piece)
        self.toggle_turn()

        key = encode_position(board.grid, self.turn, self.castling_rights, board.en_passant_target)
        self.position_counts[key] = self.position_counts.get(key, 0) + 1

        self.save_position(board)
        self.clock.switch_turn()

        if self.check_draw(key):
            self.status['is_draw'] = True
            self.status['is_gameover'] = True
        else:
            self.check_gameover(board)

        self.awaiting_promotion = None
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
        for color in ['w', 'b']:
            if self.clock.is_flagged(color):
                self.set_gameover('Time expired', winner='White' if color == 'b' else 'Black')

        if board.is_in_check(self.turn):
            if not board.has_legal_moves(self.turn):
                self.set_gameover('Checkmate', checkmate=True, winner='White' if self.turn == 'b' else 'Black')
        else:
            if not board.has_legal_moves(self.turn):
                self.set_gameover('Stalemate', stalemate=True)


        return None

    def check_draw(self, key):

        if self.position_counts[key] >= 3:
            self.set_gameover('Threefold repetition', draw=True)
            self.status['reason'] = "Threefold repetition"
            return True

        if self.halfmove_clock >= 50:
            self.set_gameover('50 move rule', draw=True)
            return True

        return False

    def update_move_counters(self, moving_piece, captured_piece):
        if moving_piece.type == 'p' or captured_piece:
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1

        if self.turn == 'b':
            self.fullmove_number += 1

    def toggle_turn(self):
        self.turn = 'b' if self.turn == 'w' else 'w'

    def save_position(self, board):
        self.history.save_position(board, self)
    def restore_position(self, board, index):
        self.history.restore_position(board, self, index)
    def step_forward(self, board):
        self.history.step_forward(self, board)
    def step_backward(self, board):
        self.history.step_backward(self, board)
    def jump_to_start(self, board):
        self.history.jump_to_start(self, board)
    def jump_to_end(self, board):
        self.history.jump_to_end(self, board)

    def set_gameover(self, reason, winner=None, checkmate=False, stalemate=False, draw=False):
        self.status.update({
            'is_gameover': True,
            'is_checkmate': checkmate,
            'is_stalemate': stalemate,
            'is_draw': draw,
            'winner': winner,
            'reason': reason
        })
        self.clock.pause()

    def reset_status(self):
        for key in self.status:
            self.status[key] = False if isinstance(self.status[key], bool) else None
