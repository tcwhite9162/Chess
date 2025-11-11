from game.piece import Piece

def parse_fen(fen_string: str, square_size: int):
    piece_map = {'P': ('w', 'p'), 'N': ('w', 'n'), 'B': ('w', 'b'),
                 'R': ('w', 'r'), 'Q': ('w', 'q'), 'K': ('w', 'k'),
                 'p': ('b', 'p'), 'n': ('b', 'n'), 'b': ('b', 'b'),
                 'r': ('b', 'r'), 'q': ('b', 'q'), 'k': ('b', 'k'),
                 }
    
    grid = []
    ranks = fen_string.split()[0].split('/')

    for rank_str in ranks:
        rank = []
        for char in rank_str:
            if char.isnumeric():
                rank.extend([None] * int(char))
            elif char in piece_map:
                color, piece_type = piece_map[char]
                rank.append(Piece(color, piece_type, square_size))
            else:
                raise ValueError("Invalid Fen Character: " + char)    
            
        if len(rank) != 8:
            raise ValueError("Rank does not have correct length: " + rank_str)
        grid.append(rank)
    
    if len(grid) != 8:
        raise ValueError("Invalid Fen string, does not have 8 ranks")

    turn, castling_string, en_passant_string, halfmove_string, fullmove_string = fen_string.split()[1:]
    
    assert turn in ('w', 'b')

    castling_rights = {'w': {'k': 'K' in castling_string, 'q': 'Q' in castling_string}, 
                       'b': {'k': 'k' in castling_string, 'q': 'q' in castling_string}}
    
    if en_passant_string == '-':
        en_passant_square = None
    else:
        file = ord(en_passant_string[0]) - ord('a')
        rank = 8 - int(ord(en_passant_string[1]))
        en_passant_square = (rank, file)
    
    halfmove_num = int(halfmove_string)
    fullmove_num = int(fullmove_string)

    return {'grid': grid,
            'turn': turn,
            'castling_rights': castling_rights,
            'en_passant_target': en_passant_square,
            'halfmove_clock': halfmove_num,
            'fullmove_number': fullmove_num}    

    
    return grid