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
