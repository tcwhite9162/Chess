# mainly for debugging and encoding move

class Move:
    def __init__(self, from_sq, to_sq, flags=0):
        # store move as 16 bit int
        # from_sq = 6 bit int 0 - 63
        # to_sq   = 6 bit int 0 - 63
        # flags   = 4 bit int (promotion, capture, castling, en-passant)
        self.data = from_sq | (to_sq << 6) | (flags << 12)

    @staticmethod
    def encode_move(from_sq, to_sq, flags=0):
        return from_sq | (to_sq << 6) | (flags << 12)

    @staticmethod
    def move_to_string(move):
        files = {0:'a', 1:'b', 2:'c', 3:'d', 4:'e', 5:'f', 6:'g', 7:'h'}
        to_square = (move >> 6) & 0x3f
        from_square = move & 0x3f

        to_file = files[to_square % 8]
        to_rank = 8 -(to_square // 8)

        from_file = files[from_square % 8]
        from_rank = 8 -(from_square // 8)

        return f"{from_file}{from_rank}{to_file}{to_rank}"

    # Helper methods to extract data
    @property
    def from_square(self):
        return self.data & 0x3F
    
    @property
    def to_square(self):
        return (self.data >> 6) & 0x3F
    
    @property
    def flags(self):
        return (self.data >> 12) & 0xF
    
    def __repr__(self):
        return f"Move({self.from_square} -> {self.to_square}, flags={self.flags})"

