from copy import deepcopy

class GameHistory:
    def __init__(self):
        self.history_index    = -1 # -1 for beginning of game
        self.position_history = [] # List of dicts containing: board, castling / en passant, turn and half / full move nums        

    def save_position(self, board, gamestate):
        if self.history_index < len(self.position_history) - 1: # trim when rewinding
            self.position_history = self.position_history[:self.history_index + 1]

        board_copy = [[piece.copy() if piece else None for piece in row] for row in board.grid]
        
        snapshot = {
            'grid':              board_copy,
            'turn':              gamestate.turn,
            'castling_rights':   deepcopy(gamestate.castling_rights),
            'en_passant_target': board.en_passant_target,
            'halfmove_clock':    gamestate.halfmove_clock,
            'fullmove_num':      gamestate.fullmove_number,
        }

        self.position_history.append(snapshot)
        self.history_index += 1

    def restore_position(self, board, gamestate, index):
        if 0 <= index < len(self.position_history):
            snapshot = self.position_history[index]

            board.grid                = snapshot['grid']
            gamestate.turn            = snapshot['turn']
            gamestate.castling_rights = deepcopy(snapshot['castling_rights'])
            board.en_passant_target   = snapshot['en_passant_target']
            gamestate.halfmove_clock  = snapshot['halfmove_clock']
            gamestate.fullmove_number = snapshot['fullmove_num']
            self.history_index        = index
            board.flag_for_redraw()

            gamestate.status['is_gameover']     = False
            gamestate.status['is_draw']         = False
            gamestate.status['is_checkmate']    = False
            gamestate.status['is_stalemate']    = False
            gamestate.status['winner']          = None
            gamestate.status['reason']          = None

    def step_forward(self, gamestate, board):
        if self.history_index < len(self.position_history) - 1:
            self.restore_position(board, gamestate, self.history_index + 1)

    def step_backward(self, gamestate, board):
        if self.history_index > 0:
            self.restore_position(board, gamestate, self.history_index - 1)
    
    def jump_to_start(self, gamestate, board):
        self.restore_position(board, gamestate, 0)
    
    def jump_to_end(self, gamestate, board):
        self.restore_position(board, gamestate, len(self.position_history) - 1)